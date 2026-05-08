# Practical 6B – Securing MongoDB: Authentication, RBAC, and TLS Encryption

---

## Introduction

In modern database systems, security is not an optional feature — it is a fundamental requirement. MongoDB, one of the most widely used NoSQL databases, stores and manages large volumes of sensitive data across a wide range of applications. Without proper security controls, a MongoDB instance is vulnerable to unauthorized access, data breaches, and man-in-the-middle attacks, all of which can have serious consequences for data confidentiality, integrity, and availability.

By default, MongoDB starts without authentication enabled, meaning any user on the network can connect and interact with the database freely. This default behavior, while convenient for development, is a significant security risk in production environments. To address this, MongoDB provides a robust set of security mechanisms including user authentication, Role-Based Access Control (RBAC), and Transport Layer Security (TLS) encryption.

This practical explores all three of these layers in a hands-on environment. Beginning with a completely open MongoDB instance, we progressively harden the database by creating an admin user, enabling authentication, defining custom roles with limited privileges, and finally encrypting all client-server communication using TLS with self-signed certificates. The practical also includes a Node.js application demo to simulate a real-world secure database connection.

## Objectives

The objectives of this practical are to:

- Understand the security risks of running MongoDB without authentication and appreciate why security hardening is necessary.
- Create and manage MongoDB users by setting up an administrative user with full database privileges.
- Enable and test authentication to ensure that only authorized users can connect to and interact with the database.
- Implement Role-Based Access Control (RBAC) by defining a custom role with specific collection-level privileges and assigning it to an application user.
- Verify RBAC enforcement by confirming that the application user can perform permitted operations while being denied access to unauthorized databases and collections.
- Generate TLS certificates using OpenSSL to establish a Certificate Authority (CA) and sign a server certificate.
- Configure MongoDB to require TLS for all incoming connections, ensuring that data in transit is encrypted.
- Test TLS enforcement by confirming that connections without the TLS flag are rejected by the server.
- Demonstrate end-to-end secure connectivity using a Node.js application that connects to MongoDB with both authentication and TLS enabled.

## Pre-requisites

Ensure you have the following installed:
- MongoDB (mongod and mongosh)
- OpenSSL
- Node.js (for the application demo)
- Two terminal windows ready

**Verify MongoDB Installation:**
```powershell
mongosh --version
mongod --version
```

---

## Step 0: Initial MongoDB Setup (Without Auth)

### Purpose
Start MongoDB without authentication to create the first admin user. This is the only time we run MongoDB without authentication.


### Terminal 1: Start MongoDB Without Auth

**Linux/Mac:**
```bash
mongod --dbpath /data/db --bind_ip 127.0.0.1 --port 27017
```
![alt text](image.png)


---

### Terminal 2: Connect with mongosh

In a new terminal:
```powershell
mongosh --host 127.0.0.1 --port 27017
```
![alt text](image-1.png)

**Expected Output:**
```
> mongosh
Connecting to:          mongodb://127.0.0.1:27017/
Using MongoDB:          7.0.0
Using Mongosh:          1.8.0
...
test>
```



---

## Step 1: Create the First Admin User

### Inside mongosh Terminal

Switch to admin database:
```javascript
use admin;
```
![alt text](image-2.png)

**Expected Output:**
```
switched to db admin
```

Create the admin user:
```javascript
db.createUser({
  user: "rootAdmin",
  pwd: "rootStrongPwd",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
});
```
![alt text](image-3.png)


Verify the user was created:
```javascript
db.system.users.find();
```
![alt text](image-4.png)


Exit mongosh:
```javascript
exit
```


---

## Step 2: Enable Authentication in mongod.conf

### Create MongoDB Configuration File


(edit `/etc/mongod.conf`):
```yaml
storage:
  dbPath: /data/db

net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: "enabled"

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
```

![alt text](image-5.png)

### Restart MongoDB

```bash
sudo systemctl restart mongod
# Or manually:
# pkill mongod
# mongod --config /etc/mongod.conf
```

![alt text](image-6.png)


---

## Step 3: Test Authentication

### Test 1: Connect with Credentials (Should Succeed)

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  -u rootAdmin -p rootStrongPwd \
  --authenticationDatabase admin
```

...
admin>
```

Inside mongosh, check connection status:
```javascript
db.runCommand({ connectionStatus: 1 });
```

![alt text](image-7.png)


Exit:
```javascript
exit
```

### Test 2: Connect Without Credentials (Should Fail)

```powershell
mongosh --host 127.0.0.1 --port 27017
```

**Expected Output:**
```
test>
```

Try to list databases:
```javascript
show dbs;
```
![alt text](image-8.png)


```javascript
exit
```

Show authentication error when connecting without credentials.

---

## Step 4: Create Application Database, Role, and User (RBAC)

### Connect as Admin

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  -u rootAdmin -p rootStrongPwd \
  --authenticationDatabase admin
```

### Create Application Database and Role

Switch to application database:
```javascript
use myapp;
```

Create a custom role for application users:
```javascript
db.runCommand({
  createRole: "myAppRole",
  privileges: [
    {
      resource: { db: "myapp", collection: "customers" },
      actions: ["find", "insert", "update", "remove"]
    }
  ],
  roles: [] // no inherited roles
});
```

![alt text](image-9.png)

Verify role creation:
```javascript
db.getRoles({ showBuiltinRoles: false });
```

![alt text](image-10.png)

### Create Application User with Limited Permissions

```javascript
db.createUser({
  user: "appUser",
  pwd: "appStrongPwd",
  roles: [
    { role: "myAppRole", db: "myapp" }
  ]
});
```

![alt text](image-11.png)

Show role and user creation output.

Exit:
```javascript
exit
```

### Test RBAC: Connect as Application User

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  -u appUser -p appStrongPwd \
  --authenticationDatabase myapp
```

Switch to myapp database:
```javascript
use myapp;
```

### Test 1: Operations That Should Succeed (RBAC - Allow)

Insert a document:
```javascript
db.customers.insertOne({ name: "Student One", city: "Phuntsholing" });
```

Find documents:
```javascript
db.customers.find();
```

Insert another document:
```javascript
db.customers.insertOne({ name: "Student Two", city: "Thimphu" });
```

Update a document:
```javascript
db.customers.updateOne(
  { name: "Student One" },
  { $set: { city: "Paro" } }
);
```

Find to verify update:
```javascript
db.customers.find();
```

![alt text](image-12.png)

### Test 2: Operations That Should Fail (RBAC - Deny)

Try to access admin database:
```javascript
use admin;
```

List users (should fail):
```javascript
db.system.users.find();
```

![alt text](image-14.png)



Try to access a different collection in myapp:
```javascript
use myapp;
db.secretdata.find();
```

![alt text](image-15.png)

Exit:
```javascript
exit
```

---

## Step 5: Enable TLS Encryption for MongoDB

### Step 5.1: Generate Self-Signed Certificates

(in `/etc/mongo/tls`):
```bash
cd /etc/mongo/tls

# 1. Generate CA private key
openssl genrsa -out ca.key 4096

# 2. Create CA certificate
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 \
  -out ca.pem \
  -subj "/C=BT/ST=Chukha/L=Phuntsholing/O=DBS302/OU=Lab/CN=mongo-lab-ca"

# 3. Generate MongoDB server key
openssl genrsa -out mongo.key 4096

# 4. Create certificate signing request (CSR)
openssl req -new -key mongo.key -out mongo.csr \
  -subj "/C=BT/ST=Chukha/L=Phuntsholing/O=DBS302/OU=Lab/CN=localhost"

# 5. Sign the certificate with CA
openssl x509 -req -in mongo.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out mongo.crt -days 365 -sha256

# 6. Combine server key and certificate into single PEM
cat mongo.key mongo.crt > mongo.pem
```

Verify certificate files:
```powershell
# Linux
ls -la /etc/mongo/tls/
```

![alt text](image-16.png)

### Step 5.2: Update MongoDB Configuration for TLS

**Update config** (`/etc/mongod.conf`):
```yaml
storage:
  dbPath: /data/db

net:
  port: 27017
  bindIp: 127.0.0.1
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongo/tls/mongo.pem
    CAFile: /etc/mongo/tls/ca.pem
    allowConnectionsWithoutCertificates: true

security:
  authorization: "enabled"

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
```
![alt text](image-17.png)

### Restart MongoDB

```bash
sudo systemctl restart mongod
```

![alt text](image-18.png)

### Step 5.3: Test TLS Connection

#### Test 1: Connect WITH TLS (Should Succeed)

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  --tls \
  --tlsCAFile C:\mongodb_tls\ca.pem \
  -u appUser -p appStrongPwd \
  --authenticationDatabase myapp
```

Test commands:
```javascript
use myapp;
db.customers.insertOne({ name: "TLS Test", city: "Thimphu" });
db.customers.find();
```

![alt text](image-19.png)

Exit:
```javascript
exit
```

#### Test 2: Connect WITHOUT TLS (Should Fail)

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  -u appUser -p appStrongPwd \
  --authenticationDatabase myapp
```

![alt text](image-20.png)
---

## Step 6: (Optional) Simple Application Code Demo for MongoDB

### Create Node.js Application

Create a file named `mongo_secure_demo.js`:

```javascript
const { MongoClient } = require("mongodb");
const fs = require("fs");

async function main() {
  // Connection string with TLS enabled
  const uri = "mongodb://appUser:appStrongPwd@127.0.0.1:27017/myapp?tls=true";

  const client = new MongoClient(uri, {
    tlsCAFile: "C:\\mongodb_tls\\ca.pem", // For Windows
    // tlsCAFile: "/etc/mongo/tls/ca.pem", // For Linux
  });

  try {
    console.log("Connecting to MongoDB with TLS and authentication...");
    await client.connect();
    console.log("✓ Successfully connected to MongoDB");

    const db = client.db("myapp");
    const customers = db.collection("customers");

    // Insert a document
    console.log("\n[1] Inserting document...");
    const insertResult = await customers.insertOne({
      name: "Node.js Client",
      city: "Phuntsholing",
      timestamp: new Date(),
    });
    console.log("✓ Inserted document with ID:", insertResult.insertedId);

    // Find all documents
    console.log("\n[2] Querying all customers...");
    const docs = await customers.find({}).toArray();
    console.log("✓ Found", docs.length, "documents:");
    docs.forEach((doc, index) => {
      console.log(`  ${index + 1}. ${doc.name} - ${doc.city}`);
    });

    // Update a document
    console.log("\n[3] Updating a document...");
    const updateResult = await customers.updateOne(
      { name: "Node.js Client" },
      { $set: { city: "Paro", updated: true } }
    );
    console.log("✓ Updated", updateResult.modifiedCount, "document");

    // Count documents
    console.log("\n[4] Counting documents...");
    const count = await customers.countDocuments();
    console.log("✓ Total customers:", count);

    // Connection info
    console.log("\n[5] Connection Status:");
    console.log("✓ Database:", db.name);
    console.log("✓ Collection:", customers.collectionName);
    console.log("✓ TLS Enabled: Yes");
    console.log("✓ Authentication: Enabled");

    console.log("\n=== Demo Completed Successfully ===");
  } catch (error) {
    console.error("Error:", error.message);
  } finally {
    await client.close();
    console.log("\nConnection closed.");
  }
}

main().catch(console.error);
```
![alt text](image-21.png)

### Install MongoDB Package

```powershell
npm install mongodb
```

### Run the Application

```powershell
node mongo_secure_demo.js
```

![alt text](image-22.png)

---

## Troubleshooting

### Issue 1: MongoDB Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
sudo lsof -i :27017
sudo kill -9 <PID>
```

---

### Issue 2: "command listDatabases requires authentication"

**This is EXPECTED** when auth is enabled and you're not authenticated.

**Solution:** Always use `-u`, `-p`, and `--authenticationDatabase` flags.

---

### Issue 3: Certificate Verification Failed

**Error:** `MongoNetworkError: SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
- Ensure `--tlsCAFile` points to correct ca.pem path
- Check file permissions on certificate files
- Use `--tlsAllowInvalidCertificates` for testing only (NOT for production)

---

### Issue 4: Connection Refused Without TLS

**Error:** `MongoNetworkError: connect ECONNREFUSED`

**Solution:** This is expected! MongoDB requires TLS. Use `--tls` flag.

---

### Issue 5: "not authorized on admin" Error

**This is EXPECTED** when restricted user tries accessing admin database.

**Solution:** Users can only access databases and collections they have privileges for. This confirms RBAC is working!

---

## Conclusion

This practical successfully demonstrated how to implement a comprehensive, multi-layered security model for MongoDB. Starting from a completely open, unauthenticated instance, the database was progressively hardened through three distinct security layers.

First, authentication was enforced by creating an admin user and restarting MongoDB with authorization: enabled in the configuration file. This ensured that all clients must present valid credentials before interacting with the database, eliminating anonymous access entirely.

Second, Role-Based Access Control (RBAC) was implemented by defining a custom role (myAppRole) that restricted an application user (appUser) to only the find, insert, update, and remove operations on a single collection (customers) within the myapp database. Attempts to access the admin database or any other collection were correctly denied, confirming that the principle of least privilege was enforced.

Third, TLS encryption was configured using self-signed certificates generated with OpenSSL. With requireTLS enabled, MongoDB rejected all non-TLS connections, and the mongosh client could only establish a session when the --tls and --tlsCAFile flags were provided. This ensures that all data transmitted between clients and the server is encrypted, protecting against eavesdropping and man-in-the-middle attacks.

Finally, the Node.js application demo validated that these security controls work seamlessly in a real-world application context, with the driver successfully authenticating and communicating over an encrypted TLS channel.
Together, these three pillars — Authentication, RBAC, and TLS — form the foundation of a production-ready MongoDB security configuration. The practical reinforced that database security is not a single feature but a layered discipline, and that each layer serves a distinct and essential role in protecting data assets.