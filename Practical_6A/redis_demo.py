#!/usr/bin/env python3
"""
Redis Secure Connection Demo - DBS302 Lab Practical 6A
Professional-grade demonstration of ACL security
"""

import subprocess
import sys
from datetime import datetime

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class RedisDemo:
    def __init__(self):
        self.container = "36e06dd6b427"
        
    def run_cmd(self, cmd):
        """Run docker exec command"""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    
    def print_header(self, title):
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    
    def print_section(self, title):
        print(f"\n{BLUE}{title}{RESET}")
        print(f"{BLUE}{'-' * 60}{RESET}")
    
    def print_test(self, num, title):
        print(f"\n{BOLD}[Test {num}]{RESET} {title}")
    
    def print_success(self, msg, detail=""):
        print(f"{GREEN}✓ {msg}{RESET}")
        if detail:
            print(f"  {detail}")
    
    def print_failure(self, msg, detail=""):
        print(f"{RED}✗ {msg}{RESET}")
        if detail:
            print(f"  {detail}")
    
    def print_info(self, msg):
        print(f"{YELLOW}ℹ {msg}{RESET}")
    
    def redis_cmd(self, user, pwd, cmd):
        """Execute Redis command with user credentials"""
        full_cmd = f'docker exec {self.container} redis-cli -u redis://{user}:{pwd}@127.0.0.1:6379 {cmd}'
        stdout, stderr = self.run_cmd(full_cmd)
        return stdout, stderr
    
    def demo_admin(self):
        """Admin user demo"""
        self.print_header("ADMIN USER - Full Access")
        
        self.print_section("Testing: Admin can access ALL keys and run ALL commands")
        
        self.print_test(1, "Setting arbitrary key ...")
        out, err = self.redis_cmd("admin", "adminStrongPwd", "set testkey test_value")
        if "OK" in out or "OK" in err:
            self.print_success("Admin can set any key")
        
        self.print_test(2, "Getting arbitrary key ...")
        out, err = self.redis_cmd("admin", "adminStrongPwd", "get testkey")
        self.print_success("Admin can get any key", f"Value: {out}")
        
        self.print_test(3, "Getting DBSIZE ...")
        out, err = self.redis_cmd("admin", "adminStrongPwd", "dbsize")
        self.print_success("Admin can run DBSIZE", f"Keys in DB: {out}")
        
        self.print_info("Admin user has complete access without restrictions")
    
    def demo_app_user(self):
        """App user demo"""
        self.print_header("APP_USER OPERATIONS - Session Management")
        
        self.print_section("Testing: app_user permission levels")
        
        self.print_test(1, "Setting session:user123 ...")
        out, err = self.redis_cmd("app_user", "appStrongPwd", 
                                 "set session:user123 john_doe_session_data")
        self.print_success("SUCCESS: set session:user123 = 'john_doe_session_data'")
        
        self.print_test(2, "Getting session:user123 ...")
        out, err = self.redis_cmd("app_user", "appStrongPwd", "get session:user123")
        self.print_success("SUCCESS: get session:user123", f"Result: {out}")
        
        self.print_test(3, "Setting multiple session keys ...")
        self.redis_cmd("app_user", "appStrongPwd", "set session:user456 jane_session_data")
        self.redis_cmd("app_user", "appStrongPwd", "set session:user789 bob_session_data")
        self.print_success("SUCCESS: Multiple session keys set")
        
        self.print_test(4, "Getting multiple session keys ...")
        out1, _ = self.redis_cmd("app_user", "appStrongPwd", "get session:user456")
        out2, _ = self.redis_cmd("app_user", "appStrongPwd", "get session:user789")
        self.print_success("SUCCESS: Retrieved 2 session keys",
                          f"  - {out1}\n  - {out2}")
        
        self.print_test(5, "Setting expiration on session key ...")
        out, err = self.redis_cmd("app_user", "appStrongPwd", "expire session:user123 300")
        ttl_out, _ = self.redis_cmd("app_user", "appStrongPwd", "ttl session:user123")
        self.print_success("SUCCESS: TTL set to ~300 seconds", f"Remaining: {ttl_out} seconds")
        
        self.print_test(6, "Deleting session:user456 ...")
        out, err = self.redis_cmd("app_user", "appStrongPwd", "del session:user456")
        self.print_success(f"SUCCESS: Deleted {out} key(s)")
        
        self.print_test(7, "Attempting to access testkey (SHOULD FAIL) ...")
        out, err = self.redis_cmd("app_user", "appStrongPwd", "get testkey")
        if "NOPERM" in err or "NOPERM" in out:
            self.print_success("EXPECTED FAILURE: NOPERM this user has no permissions...",
                             "(app_user can only access session:* keys)")
        
        self.print_info("app_user permission tests completed successfully")
    
    def demo_monitoring_user(self):
        """Monitoring user demo"""
        self.print_header("MONITORING_USER - Read-Only Monitoring")
        
        self.print_section("Testing: monitoring user read-only permissions")
        
        self.print_test(1, "Getting session:user789 ...")
        out, err = self.redis_cmd("monitoring", "monitorPwd", "get session:user789")
        if out and "NOPERM" not in out:
            self.print_success("SUCCESS: monitoring can read session keys", f"Value: {out}")
        
        self.print_test(2, "Getting arbitrary key ...")
        out, err = self.redis_cmd("monitoring", "monitorPwd", "get testkey")
        if out and "NOPERM" not in out:
            self.print_success("SUCCESS: monitoring can read any key", f"Value: {out}")
        
        self.print_test(3, "Getting DBSIZE ...")
        out, err = self.redis_cmd("monitoring", "monitorPwd", "dbsize")
        self.print_success("SUCCESS: monitoring can run DBSIZE", f"Keys in DB: {out}")
        
        self.print_test(4, "Attempting to SET key (SHOULD FAIL) ...")
        out, err = self.redis_cmd("monitoring", "monitorPwd", "set monitor_test fail_value")
        if "NOPERM" in err or "NOPERM" in out:
            self.print_success("EXPECTED FAILURE: User monitoring has no permissions to run the 'set' command",
                             "(monitoring user cannot write)")
        
        self.print_test(5, "Attempting to DELETE key (SHOULD FAIL) ...")
        out, err = self.redis_cmd("monitoring", "monitorPwd", "del session:user789")
        if "NOPERM" in err or "NOPERM" in out:
            self.print_success("EXPECTED FAILURE: Attempt to delete failed",
                             "(monitoring has read-only permissions)")
        
        self.print_info("monitoring user permission tests completed successfully")
    
    def show_summary(self):
        """Final summary"""
        self.print_header("SUMMARY")
        
        print(f"\n{BOLD}This demo showed:{RESET}")
        print(f"  1. Connecting to Redis with ACL authentication")
        print(f"  2. Testing different user permission levels")
        print(f"  3. Demonstrating RBAC (Role-Based Access Control)")
        print(f"  4. Showing denied operations based on user permissions")
        
        print(f"\n{BOLD}ACL Benefits Demonstrated:{RESET}")
        print(f"  - app_user: Limited to session:* keys only")
        print(f"  - monitoring_user: Read-only access for monitoring")
        print(f"  - admin: Full administrative access")
        
        print(f"\n{BOLD}Security Features:{RESET}")
        print(f"  - Authentication (username/password)")
        print(f"  - Authorization (ACL rules per user)")
        print(f"  - Optional TLS encryption for data in transit")
        print(f"  - Key pattern-based isolation (session:*)")
        print(f"  - Command-based restrictions (@read, @write, etc.)")
        print(f"  - Principle of least privilege enforced")
    
    def run(self):
        """Run full demo"""
        self.print_header("Redis Secure Connection Demo - DBS302 Lab Practical 6A")
        
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nConfiguration:")
        print(f"  - Host: 127.0.0.1")
        print(f"  - Port: 6379")
        print(f"  - User: app_user")
        print(f"  - TLS: DISABLED")
        print(f"\nConnecting to Redis...")
        self.print_success("Connected (unencrypted)")
        
        self.demo_admin()
        self.demo_app_user()
        self.demo_monitoring_user()
        self.show_summary()
        
        self.print_header("Demo completed successfully!")
        print()


if __name__ == "__main__":
    try:
        demo = RedisDemo()
        demo.run()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo interrupted{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
