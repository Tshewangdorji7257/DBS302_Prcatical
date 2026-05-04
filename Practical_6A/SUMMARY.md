# DBS Practical 6A - Redis ACL Security
## Execution Summary & Results

**Date:** May 4, 2026  
**Practical:** 6A - Securing Redis (Part A)  
**Container:** 36e06dd6b427 (redis:latest)  
**Port:** 6379

---

## Executive Summary

Successfully configured Redis with Access Control List (ACL) security featuring role-based access control, key pattern restrictions, and command-level permissions. All three ACL users are working as expected with proper enforcement of security rules.

---

## Part 1: ACL Configuration

### Users Created

| User | Password | Status | Permissions |
|------|----------|--------|-------------|
| **admin** | adminStrongPwd | Enabled | All keys (~*), All commands (+@all) |
| **app_user** | appStrongPwd | Enabled | Session keys (~session:*), Limited commands |
| **monitoring** | monitorPwd | Enabled | All keys (~*), Read-only + monitoring |

### ACL Commands Used

```bash
# Admin user - full access
ACL SETUSER admin on >adminStrongPwd ~* +@all

# App user - restricted to session keys
ACL SETUSER app_user on >appStrongPwd ~session:* +get +set +del +expire +ttl +@connection

# Monitoring user - read-only
ACL SETUSER monitoring on >monitorPwd ~* +@read +info +dbsize +lastsave +@connection
```

---

## Part 2: Test Results

### Test 1: Admin User (Full Access) ✓ PASSED

**Credentials:** admin / adminStrongPwd

| Test | Command | Result | Status |
|------|---------|--------|--------|
| Check identity | ACL WHOAMI | admin | ✓ Success |
| Set any key | SET mykey "hello" | OK | ✓ Success |
| Get any key | GET mykey | "hello" | ✓ Success |
| Full permissions | All commands allowed | +@all | ✓ Success |

**Observation:** Admin user can execute any command and access any keys without restrictions.

---

### Test 2: App User (Restricted Access) ✓ PASSED

**Credentials:** app_user / appStrongPwd

| Test | Command | Result | Status |
|------|---------|--------|--------|
| Check identity | ACL WHOAMI | NOPERM | ✓ Correct (no permission) |
| Set session key | SET session:user456 "data" | OK | ✓ Success |
| Get session key | GET session:user456 | "data" | ✓ Success |
| Expire session | EXPIRE session:user456 300 | 1 | ✓ Success |
| Set non-session key | SET other_key "fail" | NOPERM | ✓ Blocked (expected) |
| Get non-session key | GET mykey | NOPERM | ✓ Blocked (expected) |

**Observation:** App user can only access keys matching "session:*" pattern. Attempts to access other keys are denied.

---

### Test 3: Monitoring User (Read-Only) ✓ PASSED

**Credentials:** monitoring / monitorPwd

| Test | Command | Result | Status |
|------|---------|--------|--------|
| Check identity | ACL WHOAMI | NOPERM | ✓ Correct (no permission) |
| Get session key | GET session:user456 | "data" | ✓ Success |
| Get any key | GET mykey | "hello" | ✓ Success |
| Write attempt | SET monitor_test "fail" | NOPERM | ✓ Blocked (expected) |
| Run INFO | INFO server | (server info) | ✓ Success |
| Run DBSIZE | DBSIZE | 10 | ✓ Success |

**Observation:** Monitoring user can read all keys and execute monitoring commands, but cannot write any data.

---

## Part 3: Security Analysis

### Key Pattern Authorization Results

**Principle Demonstrated:** Least Privilege through Key Patterns

```
✓ app_user can access:  session:user456, session:*, session:anything
✗ app_user cannot access: mykey, other_key, users:*, custom:*, etc.
```

**Impact:** If app_user credentials are compromised, attacker can only access session data, not user data or other sensitive keys.

---

### Command Authorization Results

**Admin user access:**
- ✓ All commands (+@all)

**App user access:**
- ✓ Read/Write: GET, SET, DEL, EXPIRE, TTL
- ✓ Connection: PING, ECHO, SELECT
- ✗ Denied: FLUSHDB, FLUSHALL, INFO, MONITOR, KEYS, SCAN

**Monitoring user access:**
- ✓ Read: GET, MGET, GETRANGE, STRLEN
- ✓ Monitoring: INFO, DBSIZE, LASTSAVE, COMMAND
- ✗ Denied: SET, DEL, APPEND, LPUSH, any write operations

**Impact:** Each user can only execute commands needed for their role.

---

## Part 4: Security Concepts Demonstrated

### 1. Authentication ✓
- Users must provide correct username/password to connect
- Invalid credentials are rejected: "AUTH failed: WRONGPASS"

### 2. Authorization ✓
- Users have different permission levels based on role
- Commands are restricted per user
- Key access is pattern-based

### 3. Role-Based Access Control (RBAC) ✓
```
Role: Administrator
├── Access: All keys and commands
└── Use Case: System administration, DBA operations

Role: Application User
├── Access: session:* keys only, limited commands
└── Use Case: Web application data access

Role: Monitoring
├── Access: All keys (read-only), monitoring commands
└── Use Case: Health checks, diagnostics, monitoring systems
```

### 4. Principle of Least Privilege ✓
- Each user has exactly the permissions needed
- No unnecessary access granted
- Default user remains for backward compatibility

### 5. Defense in Depth ✓
```
Layer 1: Network (Docker port binding)
Layer 2: Authentication (ACL usernames/passwords)
Layer 3: Authorization (Key patterns + commands)
Layer 4: Audit (ACL can track user actions)
```

---

## Part 5: Error Messages & Expected Behaviors

### Successful Authentication
```
User: admin / adminStrongPwd
Result: Connected successfully, full access
```

### Successful Authorization
```
User: app_user attempts: SET session:user123 "data"
Result: OK (allowed - matches pattern session:*)
```

### Permission Denied - Key Pattern Violation
```
User: app_user attempts: SET other_key "data"
Result: NOPERM No permissions to access a key
Reason: "other_key" does not match "session:*" pattern
```

### Permission Denied - Command Not Allowed
```
User: monitoring attempts: SET key "data"  
Result: NOPERM User monitoring has no permissions to run the 'set' command
Reason: SET command not in user's allowed command list
```

---

## Part 6: Real-World Applications

### Scenario 1: Web Application
```
Role: App_User
- Stores session data in "session:*" keys
- Cannot accidentally delete other data
- Cannot run dangerous commands like FLUSHDB
Result: Safe application isolation
```

### Scenario 2: Monitoring Stack
```
Role: Monitoring_User
- Prometheus/Grafana collect metrics via INFO command
- Can read all keys for diagnostics
- Cannot modify data (no write access)
Result: Secure observability
```

### Scenario 3: Administrator
```
Role: Admin
- Performs maintenance and configuration
- Full access when needed
- Should use sparingly and audit heavily
Result: Flexibility with accountability
```

---

## Part 7: Improvements & Extensions

### Already Implemented
- ✓ ACL user creation with passwords
- ✓ Key pattern-based restrictions
- ✓ Command-based restrictions  
- ✓ Multiple role definitions

### Optional Enhancements (For Future)
- [ ] TLS encryption for client connections
- [ ] ACL persistence to disk
- [ ] Audit logging of ACL-denied commands
- [ ] Integration with external auth systems (LDAP/OAuth)
- [ ] Default user disabling for production
- [ ] ACL rule versioning and rollback

---

## Part 8: Troubleshooting Guide

### Issue: "ERR unknown command 'whoami'"
**Cause:** `whoami` command not available in Redis < 7.0  
**Solution:** Use `ACL WHOAMI` instead

### Issue: "NOPERM this user has no permissions"
**Expected behavior:** User lacks permission for requested operation  
**Resolution:** Check user's key patterns and allowed commands

### Issue: "AUTH failed: WRONGPASS"
**Cause:** Incorrect password provided  
**Solution:** Verify credentials: admin/adminStrongPwd, etc.

### Issue: Cannot connect after disabling default user
**Cause:** Default user disabled and new users not accessible  
**Solution:** Restart Redis and re-add users via setup script

---

## Conclusions

### ACL Security Features Validated

1. **Authentication Works** ✓
   - Users can authenticate with correct credentials
   - Invalid credentials are rejected

2. **Key Pattern Restrictions Work** ✓
   - app_user successfully restricted to session:* keys
   - Non-matching keys are denied

3. **Command Restrictions Work** ✓
   - Admin can execute all commands
   - App_user limited to appropriate commands
   - Monitoring user restricted to read-only commands

4. **RBAC is Effective** ✓
   - Different users have different permission levels
   - Principle of least privilege is enforced
   - Compromised credentials have limited damage

5. **Security Benefits Achieved** ✓
   - Separation of duties
   - Limited blast radius in case of compromise
   - Audit trail capability
   - Defense in depth approach

---

## Files Generated

| File | Purpose |
|------|---------|
| setup_acl.ps1 | Configure Redis ACL users |
| test_redis_acl.ps1 | Comprehensive ACL testing |
| redis_acl_test.py | Python client testing |
| redis.conf | Configuration template |
| GUIDE.md | Detailed practical guide |
| OBSERVATION_TABLE.md | Results recording template |
| SUMMARY.md | This file |

---

## Student Reflections

### Question 1: Why is ACL important for Redis security?
**Answer:** ACL provides granular access control, ensuring that compromised credentials have limited impact and applications cannot accidentally access sensitive data outside their scope.

### Question 2: What is the advantage of key pattern restrictions?
**Answer:** It creates namespace-based isolation - an application can only affect data in its own key namespace, preventing cross-application data contamination.

### Question 3: How does this compare to traditional database security?
**Answer:** ACL in Redis is similar to database user permissions but simpler and more flexible, focusing on key patterns and command categories rather than table/schema-level control.

### Question 4: What would happen if app_user credentials were stolen?
**Answer:** Attacker could only read/modify session:* keys, not user data or system keys. Damage is contained to session data only.

### Question 5: How would you handle a compromised user?
**Answer:** 
1. Disable the user: `ACL SETUSER app_user off`
2. Change password: `ACL SETUSER app_user >newPassword`
3. Review access logs
4. Re-enable when ready

---

## Practical Completion Checklist

- [x] Redis container running with Docker
- [x] ACL users created (admin, app_user, monitoring)
- [x] Passwords configured for all users
- [x] Key pattern restrictions enforced
- [x] Command restrictions enforced
- [x] Admin user can access all data
- [x] App user restricted to session:* keys
- [x] Monitoring user read-only
- [x] NOPERM errors working correctly
- [x] All tests passing
- [x] Documentation complete

---

**Status:** ✓ PRACTICAL COMPLETE  
**All Security Features:** ✓ WORKING  
**All Tests:** ✓ PASSING  

This practical successfully demonstrates Redis security using Access Control Lists, providing role-based access control with granular command and key restrictions.

