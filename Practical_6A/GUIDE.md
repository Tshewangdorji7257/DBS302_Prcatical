# DBS Practical 6A - Securing Redis (Part A)
## Comprehensive Guide

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Testing Procedures](#testing-procedures)
5. [Expected Behaviors](#expected-behaviors)
6. [Security Concepts](#security-concepts)

---

## Overview

This practical demonstrates Redis security features:
- **Authentication:** Users must provide credentials to connect
- **Role-Based Access Control (RBAC):** Users have different permission levels
- **Key Pattern Restrictions:** Users can only access specific key patterns
- **Command Restrictions:** Users can only execute allowed commands

### Security Model

```
        Internet / Network
              |
              v
    +-------------------+
    | Authentication    |  ← User provides username + password
    +-------------------+
              |
              v
    +-------------------+
    | Command Check     |  ← Can user run this command?
    +-------------------+
              |
              v
    +-------------------+
    | Key Pattern Check |  ← Can user access this key?
    +-------------------+
              |
              v
        Redis Database
```

---

## Prerequisites

### Requirements
- Docker installed and running
- Redis container: `36e06dd6b427` with redis:latest
- Port 6379 accessible on localhost
- Python 3.6+ (for optional Python tests)
- redis-py library: `pip install redis`

### Verify Prerequisites
```powershell
# Check Docker
docker --version

# Check Redis container
docker ps | findstr "36e06dd6b427"

# Should show something like:
# 36e06dd6b427  redis:latest  up 2 hours

# Check Redis connectivity
docker exec 36e06dd6b427 redis-cli ping
# Expected: PONG
```

---

## Setup Instructions

### Step 1: Copy redis.conf to Container

The `redis.conf` file contains ACL rules:

```powershell
# Navigate to the practical directory
cd c:\Users\Dell\Desktop\DBS_Practical\Practical_6A

# Run setup script
powershell .\setup_redis_acl.ps1
```

### What the setup script does:
1. Verifies Redis container is running
2. Copies redis.conf to `/usr/local/etc/redis/`
3. Stops the old Redis process
4. Starts Redis with the new ACL configuration
5. Verifies Redis is responding

### ACL Users Configured

| User | Role | Password | Access | Commands |
|------|------|----------|--------|----------|
| default | - | - | Off/Disabled | - |
| admin | Administrator | adminStrongPwd | All keys (~*) | All commands (+@all) |
| app_user | Application | appStrongPwd | Session keys (session:*) | get, set, del, expire, ttl, connection |
| monitoring | Monitor | monitorPwd | All keys (~*) | Read-only (+@read), info, dbsize, connection |

---

## Testing Procedures

### Quick Start: Manual Testing

#### 1. Test Admin User
```powershell
# Connect as admin
docker exec 36e06dd6b427 redis-cli -u redis://admin:adminStrongPwd@127.0.0.1:6379

# In redis-cli:
whoami                    # Shows "admin"
set any_key "any_value"   # Works
get any_key               # Works
set session:test "data"   # Works (admin can do anything)
```

#### 2. Test App User
```powershell
# Connect as app_user
docker exec 36e06dd6b427 redis-cli -u redis://app_user:appStrongPwd@127.0.0.1:6379

# In redis-cli:
whoami                       # Shows "app_user"
set session:user123 "data"   # Works (matches session:*)
get session:user123          # Works
set otherkey "fail"          # FAILS - key doesn't match session:*
get any_key                  # FAILS - key doesn't match session:*
```

#### 3. Test Monitoring User
```powershell
# Connect as monitoring
docker exec 36e06dd6b427 redis-cli -u redis://monitoring:monitorPwd@127.0.0.1:6379

# In redis-cli:
whoami                   # Shows "monitoring"
get session:user123      # Works (read-only)
get any_key              # Works (read-only)
set session:test "oops"  # FAILS - no write permission
info server              # Works (monitoring command)
dbsize                   # Works (monitoring command)
```

### Automated Testing

#### PowerShell Script
```powershell
# Run comprehensive ACL tests
.\test_acl.ps1
```

This script tests all users and commands, displaying results in a table format.

#### Python Script
```powershell
# Run Python tests (requires redis-py)
pip install redis

python redis_acl_test.py
```

This script demonstrates secure connection from Python with authentication.

---

## Expected Behaviors

### Authentication Layer
```
Scenario: User connects with wrong password
Command: redis-cli -u redis://admin:wrongpwd@127.0.0.1:6379 ping
Result: ERR invalid password

Scenario: User connects with correct password
Command: redis-cli -u redis://admin:adminStrongPwd@127.0.0.1:6379 ping
Result: PONG
```

### Key Pattern Authorization
```
Scenario: app_user tries to access session:* keys
Commands: set session:user123 "data"  ✓ Allowed
          get session:user123        ✓ Allowed
          set session:test "more"    ✓ Allowed

Scenario: app_user tries to access other keys
Commands: set mykey "hello"          ✗ Denied
          get any_key                ✗ Denied
          set users:100 "data"       ✗ Denied

Error Message:
(error) NOPERM this user has no permissions to access one of the keys used as arguments
```

### Command Authorization
```
Scenario: app_user executes allowed commands
Commands: GET, SET, DEL, EXPIRE, TTL, PING, ECHO  ✓ Allowed

Scenario: app_user executes forbidden commands
Commands: FLUSHDB, FLUSHALL, KEYS, SCAN  ✗ Denied

Scenario: monitoring user executes read commands
Commands: GET, MGET, GETRANGE, STRLEN  ✓ Allowed
          INFO, DBSIZE, LASTSAVE         ✓ Allowed

Scenario: monitoring user attempts write
Commands: SET, DEL, APPEND  ✗ Denied
```

---

## Security Concepts

### 1. Authentication
- **Definition:** Verifying user identity through credentials
- **Implementation:** Username + password checked by Redis
- **In this practical:** Each user has a unique username/password

### 2. Authorization
- **Definition:** Determining what an authenticated user can do
- **Implementation:** Redis ACL rules define permissions
- **Components:**
  - **Key patterns:** What keys can be accessed (e.g., session:*, users:*)
  - **Commands:** What operations are allowed (e.g., get, set, del)

### 3. Principle of Least Privilege
- **Definition:** Users have only the minimum permissions needed
- **Example:** app_user cannot read/modify other data
- **Benefit:** Limits damage if credentials are compromised

### 4. Role-Based Access Control (RBAC)
- **Definition:** Users are assigned roles with predefined permissions
- **Roles in this practical:**
  - Admin: Full access (system maintenance)
  - App_user: Limited access (application operations)
  - Monitoring: Read-only access (monitoring/diagnostics)

### 5. Defense in Depth
```
Layer 1: Network Firewall
         ↓ (Allow only specific IPs)
Layer 2: Authentication (Redis ACL users)
         ↓ (Correct username/password)
Layer 3: Authorization (Key patterns + commands)
         ↓ (Check permissions)
Layer 4: Data at Rest Encryption (Optional)
         ↓ (Encrypted on disk)
Layer 5: Data in Transit Encryption (TLS - Optional)
         ↓ (Encrypted over network)
Secure Redis Instance
```

---

## ACL Rule Format Reference

### User Definition Syntax
```
user <username> on|off >password|nopass ~key_pattern +command |-command
```

### Components Explained

| Component | Example | Meaning |
|-----------|---------|---------|
| `user` | user admin | Define a new user |
| Username | admin | User identifier |
| Status | on / off | Enable/disable user |
| Password | >password123 | Set password (> means hash it) |
| Key patterns | ~* | User can access these keys |
| ^ | ~session:* | Only session:* keys |
| Commands | +@all | Allow all commands |
| ^ | +get +set | Allow specific commands |
| ^ | -del | Deny specific command |

### Examples

```
# Full admin
user admin on >strongpwd ~* +@all

# Read-only monitoring
user monitor on >monitorpwd ~* +@read +info

# Restricted application user
user app on >apppwd ~app:* +get +set +del

# No access (disabled)
user audit off
```

---

## Troubleshooting

### Issue: "Authentication failed"
```
Cause: Wrong password or user doesn't exist
Fix: Check credentials in redis.conf and redis-cli command
```

### Issue: "ERR unknown user"
```
Cause: User not defined in redis.conf
Fix: Add user to redis.conf and restart Redis
```

### Issue: "NOPERM" error on allowed operations
```
Cause: User doesn't have permission for that key/command
Fix: Check ACL rules for user - expand key patterns or add commands
```

### Issue: Redis container not responding
```
Cause: Container crashed or not running
Fix: docker ps check status
     docker start 36e06dd6b427
     docker logs 36e06dd6b427 (see error details)
```

---

## Learning Outcomes

By completing this practical, students should understand:

1. ✓ **How to configure Redis ACL users**
   - Syntax of user definitions
   - How to enable/disable users
   - How to set passwords

2. ✓ **Key pattern restrictions**
   - Wildcard patterns (~*)
   - Prefix patterns (~session:*)
   - Why they're useful

3. ✓ **Command permissions**
   - Command categories (+@read, +@write, +@all)
   - Specific commands (+get, +set)
   - Denial rules (-command)

4. ✓ **Security principles**
   - Least privilege principle
   - Role-based access control
   - Defense in depth

5. ✓ **Practical authentication in applications**
   - Connection strings with credentials
   - Error handling
   - Secure credential storage

---

## Next Steps

### Optional: Enable TLS (Encrypted Communication)
See `OPTIONAL_TLS_SETUP.md` for instructions on setting up HTTPS/TLS encryption.

### Optional: Application Integration
See `redis_acl_test.py` for example of secure Python application connection.

### Further Reading
- Redis ACL documentation: https://redis.io/docs/management/acl/
- Redis Security: https://redis.io/topics/security
- OWASP: https://owasp.org/

---

## Files in This Practical

| File | Purpose |
|------|---------|
| redis.conf | Redis configuration with ACL rules |
| setup_redis_acl.ps1 | Setup script for Windows PowerShell |
| test_acl.ps1 | Comprehensive ACL testing script |
| redis_acl_test.py | Python-based ACL testing |
| OBSERVATION_TABLE.md | Student observation and results recording |
| GUIDE.md | This file |

---

## Questions for Reflection

1. **Why is the default user disabled?**
   
2. **What is the difference between app_user and monitoring user access patterns?**

3. **How would you add a new user with read-only access to users:* keys only?**

4. **What happens if someone steals the app_user password?**

5. **How does ACL compare to traditional database user permissions?**

---

**Created:** 2026
**Practical:** DBS 302 - Database Security
**Part:** 6A - Redis Security with ACL
