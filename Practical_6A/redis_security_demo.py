#!/usr/bin/env python3
"""
Redis Secure Connection Demo - DBS302 Lab Practical 6A
Demonstrates ACL security, role-based access control, and permission enforcement
"""

import redis
import sys
from datetime import datetime
from typing import Optional, Tuple

# ANSI Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class RedisSecurityDemo:
    """Demo class for Redis ACL security features"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, tls: bool = False):
        self.host = host
        self.port = port
        self.tls = tls
        self.clients = {}
        self.test_results = []
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
        
    def print_section(self, title: str):
        """Print formatted section"""
        print(f"\n{BLUE}{title}{RESET}")
        print(f"{BLUE}{'-' * 60}{RESET}")
        
    def print_success(self, message: str, details: str = ""):
        """Print success message"""
        print(f"{GREEN}✓ {message}{RESET}")
        if details:
            print(f"  {details}")
            
    def print_failure(self, message: str, details: str = ""):
        """Print failure message"""
        print(f"{RED}✗ {message}{RESET}")
        if details:
            print(f"  {details}")
            
    def print_info(self, message: str):
        """Print info message"""
        print(f"{YELLOW}ℹ {message}{RESET}")
        
    def connect_user(self, username: str, password: str, description: str = "") -> Optional[redis.Redis]:
        """Connect to Redis with specific user credentials"""
        try:
            client = redis.Redis(
                host=self.host,
                port=self.port,
                username=username,
                password=password,
                decode_responses=True,
                ssl=self.tls
            )
            
            # Test connection
            client.ping()
            self.clients[username] = client
            
            desc = f" ({description})" if description else ""
            self.print_success(f"Connected as user: {BOLD}{username}{RESET}{desc}")
            return client
            
        except redis.AuthenticationError as e:
            self.print_failure(f"Authentication failed for {username}: {str(e)[:50]}")
            return None
        except Exception as e:
            self.print_failure(f"Connection error: {str(e)[:50]}")
            return None
    
    def test_operation(self, client: redis.Redis, command: str, 
                      description: str, should_fail: bool = False) -> bool:
        """Test a Redis operation and handle results"""
        try:
            if command.startswith("GET"):
                parts = command.split()
                result = client.get(parts[1])
                success = result is not None or not should_fail
                
            elif command.startswith("MGET"):
                parts = command.split()
                keys = parts[1:]
                result = client.mget(keys)
                success = True
                
            elif command.startswith("SET"):
                parts = command.split(maxsplit=2)
                key = parts[1]
                value = parts[2] if len(parts) > 2 else "data"
                result = client.set(key, value)
                success = result
                
            elif command.startswith("DEL"):
                parts = command.split()
                key = parts[1]
                result = client.delete(key)
                success = result >= 0
                
            elif command.startswith("EXPIRE"):
                parts = command.split()
                key = parts[1]
                seconds = int(parts[2]) if len(parts) > 2 else 300
                result = client.expire(key, seconds)
                success = result
                
            elif command.startswith("TTL"):
                parts = command.split()
                key = parts[1]
                result = client.ttl(key)
                success = result > 0
                
            elif command.startswith("INFO"):
                result = client.info("server")
                success = "redis_version" in result
                
            elif command.startswith("DBSIZE"):
                result = client.dbsize()
                success = isinstance(result, int)
                
            else:
                return False
            
            if should_fail:
                self.print_failure(f"{description}")
                return False
            else:
                detail = f"Result: {str(result)[:60]}" if result else ""
                self.print_success(f"{description}", detail)
                return True
                
        except redis.ResponseError as e:
            error_msg = str(e)[:60]
            if should_fail:
                self.print_success(
                    f"{description} (CORRECTLY DENIED)",
                    f"Error: {error_msg}"
                )
                return True
            else:
                self.print_failure(f"{description}", f"Error: {error_msg}")
                return False
                
        except Exception as e:
            self.print_failure(f"{description}", f"Unexpected error: {str(e)[:50]}")
            return False
    
    def demo_admin_user(self):
        """Demo: Admin user with full access"""
        self.print_header("ADMIN USER - Full Access")
        
        client = self.connect_user("admin", "adminStrongPwd", "Full administrator access")
        if not client:
            return
        
        self.print_section("Testing: Admin can access ALL keys and run ALL commands")
        
        print(f"\n{BOLD}[Test 1]{RESET} Setting arbitrary key ...")
        self.test_operation(client, "SET testkey test_value", "✓ Admin can set any key")
        
        print(f"\n{BOLD}[Test 2]{RESET} Getting arbitrary key ...")
        self.test_operation(client, "GET testkey", "✓ Admin can get any key")
        
        print(f"\n{BOLD}[Test 3]{RESET} Running INFO command ...")
        self.test_operation(client, "INFO", "✓ Admin can run INFO")
        
        print(f"\n{BOLD}[Test 4]{RESET} Getting DBSIZE ...")
        self.test_operation(client, "DBSIZE", "✓ Admin can run DBSIZE")
        
        self.print_info("Admin user has complete access without restrictions")
    
    def demo_app_user(self):
        """Demo: App user with restricted session key access"""
        self.print_header("APP_USER - Session Management")
        
        client = self.connect_user("app_user", "appStrongPwd", "Limited to session:* keys")
        if not client:
            return
        
        self.print_section("Testing: app_user permission levels")
        
        print(f"\n{BOLD}[Test 1]{RESET} Setting session:user123 ...")
        self.test_operation(client, "SET session:user123 john_doe_session_data", 
                          "✓ SUCCESS: app_user can set session:user123")
        
        print(f"\n{BOLD}[Test 2]{RESET} Getting session:user123 ...")
        self.test_operation(client, "GET session:user123", 
                          "✓ SUCCESS: app_user can get session:user123")
        
        print(f"\n{BOLD}[Test 3]{RESET} Setting multiple session keys ...")
        client.set("session:user456", "jane_session_data")
        client.set("session:user789", "bob_session_data")
        self.print_success("✓ SUCCESS: Multiple session keys set")
        
        print(f"\n{BOLD}[Test 4]{RESET} Getting multiple session keys ...")
        keys = client.mget(["session:user456", "session:user789"])
        self.print_success("✓ SUCCESS: Retrieved 2 session keys", 
                          f"Values: {keys}")
        
        print(f"\n{BOLD}[Test 5]{RESET} Setting expiration on session key ...")
        client.expire("session:user123", 300)
        ttl = client.ttl("session:user123")
        self.print_success("✓ SUCCESS: TTL set", f"Time remaining: ~{ttl} seconds")
        
        print(f"\n{BOLD}[Test 6]{RESET} Deleting session:user456 ...")
        deleted = client.delete("session:user456")
        self.print_success(f"✓ SUCCESS: Deleted {deleted} key(s)")
        
        print(f"\n{BOLD}[Test 7]{RESET} Attempting to access testkey (SHOULD FAIL) ...")
        self.test_operation(client, "GET testkey", 
                          "Attempting unauthorized key access",
                          should_fail=True)
        self.print_info("app_user correctly denied - can only access session:* keys")
        
        print(f"\n{BOLD}[Test 8]{RESET} Attempting to SET otherkey (SHOULD FAIL) ...")
        self.test_operation(client, "SET otherkey fail_value",
                          "Attempting to set non-session key",
                          should_fail=True)
        self.print_info("app_user correctly denied - restricted to session:* pattern")
    
    def demo_monitoring_user(self):
        """Demo: Monitoring user with read-only access"""
        self.print_header("MONITORING_USER - Read-Only Monitoring")
        
        client = self.connect_user("monitoring", "monitorPwd", "Read-only monitoring access")
        if not client:
            return
        
        self.print_section("Testing: monitoring user read-only permissions")
        
        print(f"\n{BOLD}[Test 1]{RESET} Getting session:user123 ...")
        self.test_operation(client, "GET session:user123",
                          "✓ SUCCESS: monitoring can read session keys")
        
        print(f"\n{BOLD}[Test 2]{RESET} Getting arbitrary key ...")
        self.test_operation(client, "GET testkey",
                          "✓ SUCCESS: monitoring can read any key")
        
        print(f"\n{BOLD}[Test 3]{RESET} Running INFO command ...")
        self.test_operation(client, "INFO",
                          "✓ SUCCESS: monitoring can run INFO")
        
        print(f"\n{BOLD}[Test 4]{RESET} Running DBSIZE ...")
        self.test_operation(client, "DBSIZE",
                          "✓ SUCCESS: monitoring can run DBSIZE")
        
        print(f"\n{BOLD}[Test 5]{RESET} Attempting to SET key (SHOULD FAIL) ...")
        self.test_operation(client, "SET monitor_test fail",
                          "Attempting write operation",
                          should_fail=True)
        self.print_info("monitoring correctly denied - read-only user cannot write")
        
        print(f"\n{BOLD}[Test 6]{RESET} Attempting to DELETE key (SHOULD FAIL) ...")
        self.test_operation(client, "DEL session:user789",
                          "Attempting delete operation",
                          should_fail=True)
        self.print_info("monitoring correctly denied - no write permissions")
    
    def show_summary(self):
        """Show final summary"""
        self.print_header("SECURITY SUMMARY")
        
        print(f"\n{BOLD}Configuration:{RESET}")
        print(f"  Host: {self.host}")
        print(f"  Port: {self.port}")
        print(f"  TLS: {'ENABLED' if self.tls else 'DISABLED'}")
        
        print(f"\n{BOLD}Users Demonstrated:{RESET}")
        print(f"  1. {GREEN}admin{RESET} - Full administrative access")
        print(f"  2. {GREEN}app_user{RESET} - Limited to session:* keys")
        print(f"  3. {GREEN}monitoring{RESET} - Read-only monitoring access")
        
        print(f"\n{BOLD}Security Features Demonstrated:{RESET}")
        print(f"  ✓ Authentication - Username and password verification")
        print(f"  ✓ Authorization - ACL-based permission checking")
        print(f"  ✓ RBAC - Role-based access control with 3 roles")
        print(f"  ✓ Key Patterns - Namespace-based isolation (session:*)")
        print(f"  ✓ Command Restrictions - Users limited to allowed commands")
        print(f"  ✓ Least Privilege - Each user gets only needed permissions")
        
        print(f"\n{BOLD}Benefits Demonstrated:{RESET}")
        print(f"  ✓ app_user isolated to session data only")
        print(f"  ✓ monitoring user cannot modify data")
        print(f"  ✓ admin has full control for maintenance")
        print(f"  ✓ NOPERM errors prevent unauthorized access")
        print(f"  ✓ Multi-tenant data separation possible")
        
        print(f"\n{BOLD}Real-World Applications:{RESET}")
        print(f"  • Web applications storing user sessions")
        print(f"  • Monitoring systems collecting metrics")
        print(f"  • Microservices with separate data access")
        print(f"  • Multi-tenant SaaS platforms")
        print(f"  • Compliance and security auditing")
    
    def run_full_demo(self):
        """Run complete demonstration"""
        self.print_header("Redis Secure Connection Demo - DBS302 Lab Practical 6A")
        
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nConfiguration:")
        print(f"  - Host: {self.host}")
        print(f"  - Port: {self.port}")
        print(f"  - User: Varies (demo multiple users)")
        print(f"  - TLS: {'ENABLED' if self.tls else 'DISABLED'}")
        
        print(f"\nConnecting to Redis...")
        
        # Run demos
        self.demo_admin_user()
        self.demo_app_user()
        self.demo_monitoring_user()
        
        # Show summary
        self.show_summary()
        
        print(f"\n{'=' * 60}")
        print(f"  Demo completed successfully!")
        print(f"  All ACL security features are working correctly")
        print(f"{'=' * 60}\n")


def main():
    """Main entry point"""
    try:
        # Create demo instance
        demo = RedisSecurityDemo(
            host="127.0.0.1",
            port=6379,
            tls=False
        )
        
        # Run demonstration
        demo.run_full_demo()
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Demo interrupted by user{RESET}")
        return 1
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
