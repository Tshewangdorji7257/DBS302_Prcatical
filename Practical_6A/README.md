# DBS Practical 6A - Redis ACL Security

## Quick Start

### 1. Setup Redis with ACL Configuration
```powershell
powershell -ExecutionPolicy Bypass -File setup_acl.ps1
```

### 2. View Professional Demo
```powershell
powershell -ExecutionPolicy Bypass -File run_demo.ps1
```

**This shows:**
- ✓ Admin user with full access
- ✓ App user restricted to session:* keys only  
- ✓ Monitoring user with read-only access
- ✓ All permission tests with expected failures

### 3. Run Comprehensive Tests

**Option A: PowerShell automated test**
```powershell
powershell -ExecutionPolicy Bypass -File test_redis_acl.ps1
```

**Option B: Python automated test**
```powershell
python redis_acl_test.py
```

**Option C: Manual testing with redis-cli**
```powershell
# Admin user (full access)
docker exec 36e06dd6b427 redis-cli -u redis://admin:adminStrongPwd@127.0.0.1:6379

# App user (session keys only)
docker exec 36e06dd6b427 redis-cli -u redis://app_user:appStrongPwd@127.0.0.1:6379

# Monitoring user (read-only)
docker exec 36e06dd6b427 redis-cli -u redis://monitoring:monitorPwd@127.0.0.1:6379
```

### 4. Record Results
Fill in your observations in `OBSERVATION_TABLE.md`

---

## Files Included

| File | Description |
|------|-------------|
| `redis.conf` | Redis configuration with 4 ACL users |
| `setup_redis_acl.ps1` | Setup script (Windows) |
| `test_acl.ps1` | PowerShell testing script |
| `redis_acl_test.py` | Python testing script |
| `GUIDE.md` | Comprehensive guide with explanations |
| `OBSERVATION_TABLE.md` | Results recording template |
| `README.md` | This file |

---

## ACL Users

| User | Password | Access | Purpose |
|------|----------|--------|---------|
| **admin** | adminStrongPwd | All keys, All commands | Administrator |
| **app_user** | appStrongPwd | session:* keys, Limited commands | Application |
| **monitoring** | monitorPwd | All keys, Read-only commands | Monitoring |

---

## Learning Objectives

✓ Configure Redis ACL users  
✓ Implement role-based access control  
✓ Restrict access by key patterns  
✓ Restrict access by commands  
✓ Understand security principles  

---

## Verification Checklist

- [ ] Redis container is running
- [ ] Setup script executed successfully
- [ ] Admin user can access all keys
- [ ] App user can only access session:* keys
- [ ] App user cannot write to non-session keys
- [ ] Monitoring user can read all keys
- [ ] Monitoring user cannot write any keys
- [ ] All test results documented

---

## Support

For detailed explanations, see `GUIDE.md`

For questions:
1. Review the guide
2. Check redis.conf for ACL rules
3. See OBSERVATION_TABLE.md for expected outputs

---

**Practical:** DBS 302 - Database Security  
**Part:** 6A - Securing Redis with ACL  
**Status:** Ready to use
