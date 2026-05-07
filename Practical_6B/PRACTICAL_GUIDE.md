# Practical 6B – Securing MongoDB: Authentication, RBAC, and TLS Encryption

**Course:** DBS 302 – Database Security  
**Date:** May 2026  
**Objective:** Implement comprehensive MongoDB security including authentication, role-based access control (RBAC), and TLS encryption.

---

## Table of Contents
1. [Pre-requisites](#pre-requisites)
2. [Step 0: Initial MongoDB Setup (Without Auth)](#step-0-initial-mongodb-setup-without-auth)
3. [Step 1: Create Admin User](#step-1-create-the-first-admin-user)
4. [Step 2: Enable Authentication](#step-2-enable-authentication-in-mongodconf)
5. [Step 3: Test Authentication](#step-3-test-authentication)
6. [Step 4: Create Application Database, Role, and User (RBAC)](#step-4-create-application-database-role-and-user-rbac)
7. [Step 5: Enable TLS Encryption](#step-5-enable-tls-encryption-for-mongodb)
8. [Step 6: Test with Application Code](#step-6-optional-simple-application-code-demo-for-mongodb)
9. [Screenshots Checklist](#screenshots-checklist)
10. [Troubleshooting](#troubleshooting)

---

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

### Environment Setup

**On Windows**, create the data directory:
```powershell
# PowerShell as Administrator
mkdir "C:\data\db" -Force
mkdir "C:\mongodb_tls" -Force
```

**On Linux/Mac:**
```bash
sudo mkdir -p /data/db
sudo mkdir -p /etc/mongo/tls
sudo chown -R $USER /data/db
```

### Terminal 1: Start MongoDB Without Auth

**Windows:**
```powershell
# From your MongoDB bin directory or add to PATH
mongod --dbpath C:\data\db --bind_ip 127.0.0.1 --port 27017
```

**Linux/Mac:**
```bash
mongod --dbpath /data/db --bind_ip 127.0.0.1 --port 27017
```

**Expected Output:**
```
{"t":{"$date":"2026-05-06T10:00:00.000Z"},"s":"I",  "c":"CONTROL",  "id":23285,   "ctx":"initandlisten","msg":"MongoDB starting","attr":...
...
{"t":{"$date":"2026-05-06T10:00:00.000Z"},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"waiting for connections","attr":{"port":27017,"ssl":"off"}}
```

**✓ SCREENSHOT 1:** Show terminal with "waiting for connections" message.

---

### Terminal 2: Connect with mongosh

In a new terminal:
```powershell
mongosh --host 127.0.0.1 --port 27017
```

**Expected Output:**
```
> mongosh
Connecting to:          mongodb://127.0.0.1:27017/
Using MongoDB:          7.0.0
Using Mongosh:          1.8.0
...
test>
```

**✓ SCREENSHOT 2:** Show mongosh connected (prompt shows `test>`).

---

## Step 1: Create the First Admin User

### Inside mongosh Terminal

Switch to admin database:
```javascript
use admin;
```

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

**Expected Output:**
```
{ ok: 1 }
```

Verify the user was created:
```javascript
db.system.users.find();
```

**Expected Output:**
```
[
  {
    _id: 'admin.rootAdmin',
    user: 'rootAdmin',
    db: 'admin',
    credentials: { ... },
    roles: [
      { role: 'userAdminAnyDatabase', db: 'admin' },
      { role: 'dbAdminAnyDatabase', db: 'admin' },
      { role: 'readWriteAnyDatabase', db: 'admin' }
    ]
  }
]
```

Exit mongosh:
```javascript
exit
```

**✓ SCREENSHOT 3:** Show user creation output and user listing.

---

## Step 2: Enable Authentication in mongod.conf

### Create MongoDB Configuration File

**On Windows** (create at `C:\mongodb\mongod.conf`):
```yaml
storage:
  dbPath: C:\data\db

net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: "enabled"

systemLog:
  destination: file
  path: C:\mongodb\mongod.log
  quiet: false
```

**On Linux** (edit `/etc/mongod.conf`):
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

### Restart MongoDB

**Windows - Terminal 1:** Stop current mongod (Ctrl+C), then restart with config:
```powershell
mongod --config C:\mongodb\mongod.conf
```

**Linux:**
```bash
sudo systemctl restart mongod
# Or manually:
# pkill mongod
# mongod --config /etc/mongod.conf
```

**Expected Output:**
```
{"t":{"$date":"2026-05-06T10:05:00.000Z"},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"waiting for connections",...}
```

**✓ SCREENSHOT 4:** Show MongoDB restarted with auth enabled message.

---

## Step 3: Test Authentication

### Test 1: Connect with Credentials (Should Succeed)

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  -u rootAdmin -p rootStrongPwd \
  --authenticationDatabase admin
```

**Expected Output:**
```
> mongosh --host 127.0.0.1 --port 27017 -u rootAdmin -p rootStrongPwd --authenticationDatabase admin
Connecting to:          mongodb://127.0.0.1:27017/
Using MongoDB:          7.0.0
Using Mongosh:          1.8.0
...
admin>
```

Inside mongosh, check connection status:
```javascript
db.runCommand({ connectionStatus: 1 });
```

**Expected Output:**
```
{
  authInfo: {
    authenticated: true,
    authenticatedUsers: [
      {
        user: 'rootAdmin',
        db: 'admin'
      }
    ],
    authenticatedUserRoles: [
      { role: 'userAdminAnyDatabase', db: 'admin' },
      { role: 'dbAdminAnyDatabase', db: 'admin' },
      { role: 'readWriteAnyDatabase', db: 'admin' }
    ]
  },
  ok: 1
}
```

**✓ SCREENSHOT 5:** Show authenticated connection status output.

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

**Expected Output (Error):**
```
MongoServerError: command listDatabases requires authentication
```

This confirms authentication is working!

```javascript
exit
```

**✓ SCREENSHOT 6:** Show authentication error when connecting without credentials.

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

**Expected Output:**
```
{ ok: 1 }
```

Verify role creation:
```javascript
db.getRoles({ showBuiltinRoles: false });
```

**Expected Output:**
```
[
  {
    _id: 'myapp.myAppRole',
    role: 'myAppRole',
    db: 'myapp',
    privileges: [
      {
        resource: { db: 'myapp', collection: 'customers' },
        actions: [ 'find', 'insert', 'update', 'remove' ]
      }
    ],
    roles: [],
    inheritedPrivileges: [...]
  }
]
```

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

**Expected Output:**
```
{ ok: 1 }
```

**✓ SCREENSHOT 7:** Show role and user creation output.

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

**Expected Output:**
```
{
  acknowledged: true,
  insertedId: ObjectId('...')
}
```

Find documents:
```javascript
db.customers.find();
```

**Expected Output:**
```
[ { _id: ObjectId('...'), name: 'Student One', city: 'Phuntsholing' } ]
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

**Expected Output:**
```
{
  acknowledged: true,
  modifiedCount: 1,
  upsertedId: null
}
```

Find to verify update:
```javascript
db.customers.find();
```

**✓ SCREENSHOT 8:** Show insert, find, and update operations succeeding.

### Test 2: Operations That Should Fail (RBAC - Deny)

Try to access admin database:
```javascript
use admin;
```

List users (should fail):
```javascript
db.system.users.find();
```

**Expected Output (Error):**
```
MongoServerError: not authorized on admin to execute command { find: "system.users" }
```

Try to access a different collection in myapp:
```javascript
use myapp;
db.secretdata.find();
```

**Expected Output (Error):**
```
MongoServerError: not authorized on myapp to execute command { find: "secretdata" }
```

**✓ SCREENSHOT 9:** Show authorization errors when accessing unauthorized resources.

Exit:
```javascript
exit
```

---

## Step 5: Enable TLS Encryption for MongoDB

### Step 5.1: Generate Self-Signed Certificates

**Windows PowerShell** (in C:\mongodb_tls):
```powershell
cd C:\mongodb_tls

# 1. Generate CA private key
openssl genrsa -out ca.key 4096

# 2. Create CA certificate
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 `
  -out ca.pem `
  -subj "/C=BT/ST=Chukha/L=Phuntsholing/O=DBS302/OU=Lab/CN=mongo-lab-ca"

# 3. Generate MongoDB server key
openssl genrsa -out mongo.key 4096

# 4. Create certificate signing request (CSR)
openssl req -new -key mongo.key -out mongo.csr `
  -subj "/C=BT/ST=Chukha/L=Phuntsholing/O=DBS302/OU=Lab/CN=localhost"

# 5. Sign the certificate with CA
openssl x509 -req -in mongo.csr -CA ca.pem -CAkey ca.key -CAcreateserial `
  -out mongo.crt -days 365 -sha256

# 6. Combine server key and certificate into single PEM
Get-Content mongo.key, mongo.crt | Set-Content mongo.pem
```

**Linux/Mac** (in `/etc/mongo/tls`):
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

**Expected Output:**
```
Signature ok
subject=C = BT, ST = Chukha, L = Phuntsholing, O = DBS302, OU = Lab, CN = localhost
Getting CA Private Key
```

Verify certificate files:
```powershell
# Windows
ls C:\mongodb_tls

# Linux
ls -la /etc/mongo/tls/
```

**✓ SCREENSHOT 10:** Show certificate files created (ca.pem, mongo.pem, etc.).

### Step 5.2: Update MongoDB Configuration for TLS

**Update Windows config** (`C:\mongodb\mongod.conf`):
```yaml
storage:
  dbPath: C:\data\db

net:
  port: 27017
  bindIp: 127.0.0.1
  tls:
    mode: requireTLS
    certificateKeyFile: C:\mongodb_tls\mongo.pem
    CAFile: C:\mongodb_tls\ca.pem
    allowConnectionsWithoutCertificates: true

security:
  authorization: "enabled"

systemLog:
  destination: file
  path: C:\mongodb\mongod.log
  quiet: false
```

**Update Linux config** (`/etc/mongod.conf`):
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

### Restart MongoDB

**Windows Terminal 1:** Stop MongoDB (Ctrl+C) and restart:
```powershell
mongod --config C:\mongodb\mongod.conf
```

**Linux:**
```bash
sudo systemctl restart mongod
```

**Expected Output:**
```
{"t":{"$date":"2026-05-06T10:15:00.000Z"},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"waiting for connections",...}
```

**✓ SCREENSHOT 11:** Show MongoDB restarted with TLS enabled.

### Step 5.3: Test TLS Connection

#### Test 1: Connect WITH TLS (Should Succeed)

```powershell
mongosh --host 127.0.0.1 --port 27017 \
  --tls \
  --tlsCAFile C:\mongodb_tls\ca.pem \
  -u appUser -p appStrongPwd \
  --authenticationDatabase myapp
```

**Expected Output:**
```
> mongosh --host 127.0.0.1 --port 27017 --tls --tlsCAFile C:\mongodb_tls\ca.pem -u appUser -p appStrongPwd --authenticationDatabase myapp
Connecting to:          mongodb://127.0.0.1:27017/
Using MongoDB:          7.0.0
Using Mongosh:          1.8.0
...
myapp>
```

Test commands:
```javascript
use myapp;
db.customers.insertOne({ name: "TLS Test", city: "Thimphu" });
db.customers.find();
```

**Expected Output:**
```
{
  acknowledged: true,
  insertedId: ObjectId('...')
}

[
  { _id: ObjectId('...'), name: 'Student One', city: 'Paro' },
  { _id: ObjectId('...'), name: 'Student Two', city: 'Thimphu' },
  { _id: ObjectId('...'), name: 'TLS Test', city: 'Thimphu' }
]
```

**✓ SCREENSHOT 12:** Show successful TLS + Auth connection and data operations.

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

**Expected Output (Connection Error):**
```
MongoNetworkError: connect ECONNREFUSED 127.0.0.1:27017
```

or

```
MongoError: TLS handshake failed
```

**✓ SCREENSHOT 13:** Show connection failure without TLS flag.

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

### Install MongoDB Package

```powershell
npm install mongodb
```

### Run the Application

```powershell
node mongo_secure_demo.js
```

**Expected Output:**
```
Connecting to MongoDB with TLS and authentication...
✓ Successfully connected to MongoDB

[1] Inserting document...
✓ Inserted document with ID: ObjectId(...)

[2] Querying all customers...
✓ Found 4 documents:
  1. Student One - Paro
  2. Student Two - Thimphu
  3. TLS Test - Thimphu
  4. Node.js Client - Phuntsholing

[3] Updating a document...
✓ Updated 1 document

[4] Counting documents...
✓ Total customers: 4

[5] Connection Status:
✓ Database: myapp
✓ Collection: customers
✓ TLS Enabled: Yes
✓ Authentication: Enabled

=== Demo Completed Successfully ===

Connection closed.
```

**✓ SCREENSHOT 14:** Show Node.js application output with successful TLS + Auth connection.

---

## Screenshots Checklist

### Required Screenshots for Lab Report:

| # | Screenshot | Description |
|---|---|---|
| 1 | MongoDB Start Without Auth | Terminal showing "waiting for connections" |
| 2 | mongosh Connected | Terminal prompt showing `test>` |
| 3 | Admin User Created | User creation confirmation and listing |
| 4 | MongoDB Restarted with Auth | Restart confirmation with security enabled |
| 5 | Authenticated Connection | connectionStatus output showing authenticated user |
| 6 | Authentication Failed | Error when connecting without credentials |
| 7 | Role and User Creation | RBAC role and application user creation |
| 8 | RBAC Success Operations | Insert, find, update operations as appUser |
| 9 | RBAC Denied Operations | Authorization errors for unauthorized resources |
| 10 | TLS Certificates Generated | Certificate files in directory listing |
| 11 | MongoDB Restarted with TLS | Restart confirmation with TLS enabled |
| 12 | TLS + Auth Success | Successful connection with TLS and authentication |
| 13 | TLS Connection Failure | Error when connecting without TLS flag |
| 14 | Node.js Application Demo | Application output showing TLS + Auth operations |

**Total: 14 screenshots minimum**

---

## Troubleshooting

### Issue 1: MongoDB Port Already in Use

**Error:** `Address already in use`

**Solution:**
```powershell
# Windows - Kill MongoDB on port 27017
Get-Process mongod | Stop-Process -Force
# or specific port:
netstat -ano | findstr :27017
taskkill /PID <PID> /F
```

**Linux:**
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

## Security Summary

### What We've Implemented:

✓ **Authentication** – Users must provide valid username and password  
✓ **RBAC** – Users have specific roles with limited permissions  
✓ **TLS Encryption** – All data in transit is encrypted  
✓ **Multi-user Model** – Admin and application users with different privileges  

### Security Best Practices Demonstrated:

1. **Never run MongoDB without auth in production**
2. **Use strong passwords** (we used simple ones for the lab)
3. **Create limited roles** for application users
4. **Enable TLS** for all connections
5. **Separate admin and application users**
6. **Restrict collection access** using privileges

---

## Conclusion

This practical demonstrates a complete MongoDB security setup with:
- Initial admin user creation
- Authentication enforcement
- Role-Based Access Control (RBAC)
- TLS encryption for secure communications
- Real-world application integration

All three pillars of MongoDB security (Authentication, RBAC, TLS) are now implemented and tested!

