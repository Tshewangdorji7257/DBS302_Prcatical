# Practical 6B – Securing MongoDB with Compass: Authentication, RBAC, and TLS Encryption

**Course:** DBS 302 – Database Security  
**Date:** May 2026  
**Tool:** MongoDB Compass (GUI)  
**Objective:** Implement comprehensive MongoDB security including authentication, role-based access control (RBAC), and TLS encryption using Compass.

---

## Table of Contents
1. [Pre-requisites](#pre-requisites)
2. [Step 0: Initial MongoDB Setup (Without Auth)](#step-0-initial-mongodb-setup-without-auth)
3. [Step 1: Create Admin User](#step-1-create-the-first-admin-user)
4. [Step 2: Enable Authentication](#step-2-enable-authentication-in-mongodconf)
5. [Step 3: Test Authentication](#step-3-test-authentication)
6. [Step 4: Create Application Database, Role, and User (RBAC)](#step-4-create-application-database-role-and-user-rbac)
7. [Step 5: Enable TLS Encryption](#step-5-enable-tls-encryption-for-mongodb)
8. [Screenshots Checklist](#screenshots-checklist)
9. [Troubleshooting](#troubleshooting)

---

## Pre-requisites

Ensure you have:
- **MongoDB Server** installed (mongod)
- **MongoDB Compass** installed (GUI tool)
- **OpenSSL** installed (for certificate generation)
- Two terminal/command windows ready (one for MongoDB server, one for operations)

**Download MongoDB Compass:** https://www.mongodb.com/products/compass

---

## Step 0: Initial MongoDB Setup (Without Auth)

### Purpose
Start MongoDB without authentication to create the first admin user. We'll use Compass to connect and manage it.

### Environment Setup

**On Windows**, create the data directory:
```powershell
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
mongod --dbpath C:\data\db --bind_ip 127.0.0.1 --port 27017
```

**Linux/Mac:**
```bash
mongod --dbpath /data/db --bind_ip 127.0.0.1 --port 27017
```

**Expected Output:**
```
{"t":{"$date":"2026-05-06T10:00:00.000Z"},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"waiting for connections"...}
```

**✓ SCREENSHOT 1:** Terminal showing "waiting for connections" message.

---

### Connect with MongoDB Compass

1. **Open MongoDB Compass**
2. Click **"New Connection"**
3. Enter connection string:
   ```
   mongodb://127.0.0.1:27017
   ```
4. Click **"Connect"**

**Expected Result:** Connected to MongoDB server, see "admin", "config", "local" databases

**✓ SCREENSHOT 2:** Compass showing connected status and available databases.

---

## Step 1: Create the First Admin User

### Inside MongoDB Compass

**Step 1: Navigate to Admin Database**
1. In left sidebar, click on **"admin"** database
2. It will expand showing collections
3. Click on **"System"** folder to reveal system collections

**Step 2: Access Users Collection**
1. Expand the **"admin"** database
2. Look for **"system.users"** collection (may be hidden)
3. If not visible, enable "Show system collections":
   - Click database settings icon (⚙️)
   - Check "Show system collections"

**Step 3: Create Admin User via Atlas CLI/Mongosh Shell Tab**

Click the **">_"** icon (Shell/Console) at the bottom of Compass to open the embedded shell:

```javascript
use admin;

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

**Step 4: Verify User Created**
```javascript
db.system.users.find();
```

**Expected Output:** Document showing rootAdmin user with roles

**✓ SCREENSHOT 3:** Show the embedded shell with user creation output and db.system.users.find() results.

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

**Terminal 1:** Stop current mongod (Ctrl+C), then restart:

**Windows:**
```powershell
mongod --config C:\mongodb\mongod.conf
```

**Linux:**
```bash
mongod --config /etc/mongod.conf
```

**✓ SCREENSHOT 4:** Terminal showing MongoDB restarted with auth enabled.

---

## Step 3: Test Authentication

### Test 1: Connect with Credentials (Should Succeed)

**In MongoDB Compass:**
1. Click **"Connect"** at top
2. Edit connection string to:
   ```
   mongodb://rootAdmin:rootStrongPwd@127.0.0.1:27017/admin
   ```
3. Or use the **"Advanced Options"**:
   - **Username:** rootAdmin
   - **Password:** rootStrongPwd
   - **Authentication Database:** admin
4. Click **"Connect"**

**Expected Result:** Successfully connected, can see databases

**✓ SCREENSHOT 5:** Compass showing authenticated connection with databases visible.

---

### Test 2: Connect Without Credentials (Should Fail)

**In MongoDB Compass:**
1. Click **"New Connection"**
2. Try:
   ```
   mongodb://127.0.0.1:27017
   ```
3. Click **"Connect"**

**Expected Result:** Connection fails with authentication error

**✓ SCREENSHOT 6:** Error message showing authentication is required.

---

## Step 4: Create Application Database, Role, and User (RBAC)

### Connect as Admin First

Make sure connected with rootAdmin credentials (see Step 3, Test 1)

### Create Application Database

**In Compass:**
1. Click **"+"** button next to database list
2. Create new database:
   - **Database Name:** myapp
   - **Collection Name:** customers
   - Click **"Create Database"**

**✓ SCREENSHOT 7:** New database "myapp" created with "customers" collection.

---

### Create Custom Role

**Open Compass Shell (">_" button)** and run:

```javascript
use myapp;

db.runCommand({
  createRole: "myAppRole",
  privileges: [
    {
      resource: { db: "myapp", collection: "customers" },
      actions: ["find", "insert", "update", "remove"]
    }
  ],
  roles: []
});
```

**Expected Output:**
```
{ ok: 1 }
```

**Verify Role Created:**
```javascript
db.getRoles({ showBuiltinRoles: false });
```

**✓ SCREENSHOT 8:** Shell showing role creation success.

---

### Create Application User

**In Compass Shell:**

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

**✓ SCREENSHOT 9:** User creation confirmation in shell.

---

## Step 5: Enable TLS Encryption for MongoDB

### Step 5.1: Generate Self-Signed Certificates

**Open Terminal/Command Prompt** (not Compass):

**Windows PowerShell:**
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

**Linux/Mac:**
```bash
cd /etc/mongo/tls

openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 \
  -out ca.pem \
  -subj "/C=BT/ST=Chukha/L=Phuntsholing/O=DBS302/OU=Lab/CN=mongo-lab-ca"

openssl genrsa -out mongo.key 4096
openssl req -new -key mongo.key -out mongo.csr \
  -subj "/C=BT/ST=Chukha/L=Phuntsholing/O=DBS302/OU=Lab/CN=localhost"

openssl x509 -req -in mongo.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out mongo.crt -days 365 -sha256

cat mongo.key mongo.crt > mongo.pem
```

**Verify certificates created:**
```powershell
ls C:\mongodb_tls\  # Windows
ls /etc/mongo/tls/  # Linux
```

**✓ SCREENSHOT 10:** Directory listing showing certificate files (ca.pem, mongo.pem, etc.).

---

### Step 5.2: Update MongoDB Configuration for TLS

**Edit mongod.conf:**

**Windows** (`C:\mongodb\mongod.conf`):
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
```

**Linux** (`/etc/mongod.conf`):
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

**Terminal:** Stop MongoDB (Ctrl+C) and restart:

**Windows:**
```powershell
mongod --config C:\mongodb\mongod.conf
```

**Linux:**
```bash
mongod --config /etc/mongod.conf
```

**✓ SCREENSHOT 11:** Terminal showing MongoDB restarted with TLS enabled.

---

### Step 5.3: Test TLS Connection in Compass

#### Test 1: Connect WITH TLS (Should Succeed)

**In MongoDB Compass:**

1. Click **"New Connection"**
2. Click **"Advanced Options"**
3. Fill in:
   - **Username:** appUser
   - **Password:** appStrongPwd
   - **Authentication Database:** myapp
4. Go to **"TLS"** tab
5. Toggle **"TLS"** to **"ON"**
6. Set **"TLS CA"** to your ca.pem file path:
   - Windows: `C:\mongodb_tls\ca.pem`
   - Linux: `/etc/mongo/tls/ca.pem`
7. Click **"Connect"**

**Expected Result:** Connection succeeds, you see myapp database with customers collection

**✓ SCREENSHOT 12:** Compass showing successful TLS + Auth connection.

---

#### Test 2: Verify Data Operations with RBAC

**In Compass:**

1. Navigate to **myapp** → **customers** collection
2. Click **"Insert Document"**
3. Add:
   ```json
   { name: "Student One", city: "Phuntsholing" }
   ```
4. Click **"Insert"**

**Expected Result:** Document inserted successfully

**Step 2: Query Documents**
1. View the **customers** collection
2. Should see the inserted document

**Step 3: Try Unauthorized Operation**
1. Click **"Add Database"**
2. Try to create admin database
3. Or in Compass Shell, try:
   ```javascript
   use admin;
   db.system.users.find();
   ```

**Expected Result:** Error showing "not authorized"

**✓ SCREENSHOT 13:** Show authorized operations (insert/find in customers) and denied operations (admin access).

---

#### Test 3: Connect WITHOUT TLS (Should Fail)

**In MongoDB Compass:**

1. Click **"New Connection"**
2. Fill in without TLS:
   - **Connection String:** `mongodb://appUser:appStrongPwd@127.0.0.1:27017/myapp`
   - Or username/password fields without TLS
3. Make sure **TLS is OFF**
4. Click **"Connect"**

**Expected Result:** Connection fails with TLS handshake error

**✓ SCREENSHOT 14:** Error message showing TLS is required.

---

## Screenshots Checklist

### Required: 14 Screenshots

| # | Screenshot | Description |
|---|---|---|
| 1 | MongoDB Start | Terminal showing "waiting for connections" |
| 2 | Compass Connected | Compass showing databases without auth |
| 3 | Admin User Created | Shell output showing user creation |
| 4 | MongoDB Restarted | Terminal with auth enabled |
| 5 | Authenticated Connection | Compass connected with credentials |
| 6 | Authentication Error | Error when connecting without credentials |
| 7 | Database & Collection Created | myapp.customers visible in Compass |
| 8 | RBAC Role Created | Shell output showing role creation |
| 9 | RBAC User Created | Shell output showing user creation |
| 10 | Certificates Generated | Directory listing of certificate files |
| 11 | MongoDB Restarted with TLS | Terminal showing TLS enabled |
| 12 | TLS Connection Success | Compass connected with TLS + Auth |
| 13 | RBAC Operations | Insert/find succeed, admin access denied |
| 14 | TLS Connection Failure | Error when connecting without TLS |

---

## Lab Report Structure

### Section 1: Introduction
- Explain three pillars of MongoDB security
- Mention using Compass as the GUI tool

### Section 2: Setup
- Screenshots 1-2: MongoDB and Compass setup
- Explain authentication configuration

### Section 3: Authentication
- Screenshots 5-6: Auth success and failure
- Explain how authentication works

### Section 4: RBAC
- Screenshots 7-9: Database, role, and user creation
- Screenshots 13: Allowed vs denied operations

### Section 5: TLS Encryption
- Screenshots 10-12: Certificates and TLS connection
- Screenshot 14: TLS required verification

### Section 6: Conclusion
- Summary of what was learned
- Real-world applications

---

## Troubleshooting

### Issue 1: Compass Can't Connect to MongoDB

**Error:** "Could not connect to any servers matching your query"

**Solution:**
- Verify MongoDB is running in Terminal
- Check port 27017 is correct
- Verify connection string: `mongodb://127.0.0.1:27017`

---

### Issue 2: "requires authentication" Error

**This is EXPECTED** when auth is enabled.

**Solution:** Use credentials in Compass:
- Username: rootAdmin or appUser
- Password: corresponding password
- Authentication Database: admin (for rootAdmin) or myapp (for appUser)

---

### Issue 3: "not authorized" Error in Shell

**This is EXPECTED** - RBAC is working!

**Solution:**
- Use appropriate user for the operation
- appUser can only access myapp.customers
- rootAdmin can access everything

---

### Issue 4: TLS Connection Fails

**Error:** "TLS handshake failed"

**Solution:**
- Enable TLS toggle in Compass Advanced Options
- Provide CA certificate path
- Ensure certificate files exist

---

### Issue 5: "Certificate verify failed"

**Error:** When connecting with TLS

**Solution:**
- Verify ca.pem path is correct
- Check file exists: `ls C:\mongodb_tls\ca.pem`
- Or use "Insecure TLS" toggle for lab (not production!)

---

## Summary

This practical demonstrates complete MongoDB security using the GUI tool Compass:

✓ **Authentication** – Users must log in  
✓ **RBAC** – Users have specific permissions  
✓ **TLS Encryption** – Data is encrypted in transit  

All three security pillars are implemented and tested through Compass's intuitive interface!

