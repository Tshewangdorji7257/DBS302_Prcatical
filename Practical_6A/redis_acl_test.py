#!/usr/bin/env python3
"""
redis_acl_test.py - Test Redis ACL functionality using Python
Demonstrates connection with ACL credentials and various permission levels
"""

import redis
import sys

def test_admin_user():
    """Test admin user with full access"""
    print("\n" + "="*60)
    print("[Test 1] Admin User - Full Access")
    print("="*60)
    
    try:
        client = redis.Redis(
            host="127.0.0.1",
            port=6379,
            username="admin",
            password="adminStrongPwd",
            decode_responses=True
        )
        
        print(f"✓ Connected as: {client.acl_whoami()}")
        
        # Set and get keys
        client.set("admin_test_key", "admin_data")
        print(f"✓ SET admin_test_key: OK")
        
        value = client.get("admin_test_key")
        print(f"✓ GET admin_test_key: {value}")
        
        # Set multiple keys (admin can do anything)
        client.set("session:admin_test", "session_data")
        print(f"✓ SET session:admin_test: OK")
        
        client.set("custom:key", "custom_data")
        print(f"✓ SET custom:key: OK")
        
        # List all keys
        keys = client.keys("*")
        print(f"✓ Keys in database: {len(keys)} keys found")
        
    except redis.AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_app_user():
    """Test app_user with limited session key access"""
    print("\n" + "="*60)
    print("[Test 2] App User - Session Key Access Only")
    print("="*60)
    
    try:
        client = redis.Redis(
            host="127.0.0.1",
            port=6379,
            username="app_user",
            password="appStrongPwd",
            decode_responses=True
        )
        
        print(f"✓ Connected as: {client.acl_whoami()}")
        
        # Should succeed: session key operations
        try:
            client.set("session:user123", "user_data")
            print(f"✓ SET session:user123: OK (allowed)")
            
            value = client.get("session:user123")
            print(f"✓ GET session:user123: {value}")
            
            client.expire("session:user123", 300)
            print(f"✓ EXPIRE session:user123 300: OK")
            
            ttl = client.ttl("session:user123")
            print(f"✓ TTL session:user123: {ttl} seconds")
            
        except redis.ResponseError as e:
            print(f"✗ Session operation failed: {e}")
        
        # Should fail: non-session key operations
        print("\n  Testing non-session key access (should fail):")
        
        try:
            client.set("otherkey", "should_fail")
            print(f"✗ SET otherkey: Unexpectedly succeeded!")
        except redis.ResponseError as e:
            print(f"✓ SET otherkey: Correctly denied - {str(e)[:50]}...")
        
        try:
            value = client.get("admin_test_key")
            print(f"✗ GET admin_test_key: Unexpectedly succeeded!")
        except redis.ResponseError as e:
            print(f"✓ GET admin_test_key: Correctly denied - {str(e)[:50]}...")
        
    except redis.AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_monitoring_user():
    """Test monitoring user with read-only access"""
    print("\n" + "="*60)
    print("[Test 3] Monitoring User - Read-Only Access")
    print("="*60)
    
    try:
        client = redis.Redis(
            host="127.0.0.1",
            port=6379,
            username="monitoring",
            password="monitorPwd",
            decode_responses=True
        )
        
        print(f"✓ Connected as: {client.acl_whoami()}")
        
        # Read operations should succeed
        try:
            value = client.get("session:user123")
            print(f"✓ GET session:user123: {value} (read allowed)")
            
            value = client.get("admin_test_key")
            print(f"✓ GET admin_test_key: {value} (read allowed)")
            
            info = client.info("server")
            print(f"✓ INFO server: OK (monitoring command allowed)")
            
            dbsize = client.dbsize()
            print(f"✓ DBSIZE: {dbsize} keys")
            
        except redis.ResponseError as e:
            print(f"✗ Read operation failed: {e}")
        
        # Write operations should fail
        print("\n  Testing write access (should fail):")
        
        try:
            client.set("monitoring_test", "should_fail")
            print(f"✗ SET monitoring_test: Unexpectedly succeeded!")
        except redis.ResponseError as e:
            print(f"✓ SET monitoring_test: Correctly denied - {str(e)[:50]}...")
        
    except redis.AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_invalid_credentials():
    """Test invalid credentials"""
    print("\n" + "="*60)
    print("[Test 4] Invalid Credentials")
    print("="*60)
    
    try:
        client = redis.Redis(
            host="127.0.0.1",
            port=6379,
            username="invalid_user",
            password="invalid_password",
            decode_responses=True
        )
        client.ping()
        print("✗ Connection succeeded with invalid credentials!")
    except redis.AuthenticationError as e:
        print(f"✓ Authentication correctly rejected: {str(e)[:60]}...")
    except Exception as e:
        print(f"✓ Connection failed: {type(e).__name__}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Redis ACL Security Testing")
    print("="*60)
    
    try:
        test_admin_user()
        test_app_user()
        test_monitoring_user()
        test_invalid_credentials()
        
        print("\n" + "="*60)
        print("Testing Complete!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
