#!/usr/bin/env python3
"""
REDOPS Scope Enforcer
Hard stop if target not in authorized scope.
Run before EVERY tool execution.
"""

import sys
import json
import ipaddress
import re
from pathlib import Path
from datetime import datetime

SCOPE_FILE = Path(__file__).parent.parent / "state" / "scope.txt"
LOG_FILE = Path(__file__).parent.parent / "wiki" / "log.md"
STATE_FILE = Path(__file__).parent.parent / "state" / "session.json"

BANNER = """
╔══════════════════════════════════════╗
║     REDOPS SCOPE ENFORCER v1.0      ║
║  Unauthorized testing = illegal.     ║
║  Always verify authorization first. ║
╚══════════════════════════════════════╝
"""

def log_violation(target, reason):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"\n## [{ts}] SCOPE_VIOLATION | Target: {target} | Reason: {reason}\n")
    print(f"[!!!] SCOPE VIOLATION LOGGED: {target} — {reason}")

def load_scope():
    if not SCOPE_FILE.exists():
        print("[!!!] CRITICAL: state/scope.txt not found!")
        print("      Create it with authorized targets before proceeding.")
        print("      See: state/scope.txt.example")
        sys.exit(1)
    
    with open(SCOPE_FILE) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    return lines

def is_ip_in_scope(target_ip, scope_entries):
    """Check if IP is in scope (handles CIDR ranges)"""
    try:
        target = ipaddress.ip_address(target_ip)
    except ValueError:
        return False
    
    for entry in scope_entries:
        try:
            # CIDR network
            if '/' in entry:
                network = ipaddress.ip_network(entry, strict=False)
                if target in network:
                    return True
            # IP range: 10.10.10.1-10.10.10.50
            elif '-' in entry and entry.count('.') == 3:
                start_ip, end_ip = entry.split('-')
                start = ipaddress.ip_address(start_ip.strip())
                end = ipaddress.ip_address(end_ip.strip())
                if start <= target <= end:
                    return True
            # Single IP
            else:
                if target == ipaddress.ip_address(entry):
                    return True
        except ValueError:
            continue
    return False

def is_domain_in_scope(target, scope_entries):
    """Check if domain is in scope (handles wildcards)"""
    target = target.lower().strip()
    
    for entry in scope_entries:
        entry = entry.lower().strip()
        # Wildcard: *.example.com
        if entry.startswith('*.'):
            base = entry[2:]
            if target.endswith('.' + base) or target == base:
                return True
        # Exact match
        elif target == entry:
            return True
        # Subdomain of in-scope domain
        elif target.endswith('.' + entry):
            return True
    return False

def check_scope(target):
    scope = load_scope()
    
    # Determine target type
    is_ip = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target)
    
    if is_ip:
        in_scope = is_ip_in_scope(target, scope)
    else:
        # Strip http/https/path
        domain = re.sub(r'^https?://', '', target)
        domain = domain.split('/')[0].split(':')[0]
        in_scope = is_domain_in_scope(domain, scope)
    
    return in_scope, scope

def main():
    print(BANNER)
    
    if len(sys.argv) < 2:
        print("Usage: scope.py <target_ip_or_domain>")
        print("       scope.py --list")
        print("       scope.py --add <target>")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        scope = load_scope()
        print("=== Current Scope ===")
        for entry in scope:
            print(f"  ✓ {entry}")
        print(f"\nTotal: {len(scope)} entries")
        return
    
    if sys.argv[1] == '--add':
        if len(sys.argv) < 3:
            print("Usage: scope.py --add <target>")
            sys.exit(1)
        target = sys.argv[2]
        with open(SCOPE_FILE, 'a') as f:
            f.write(f"\n{target}")
        print(f"[+] Added to scope: {target}")
        return
    
    target = sys.argv[1]
    in_scope, scope = check_scope(target)
    
    if in_scope:
        print(f"[✓] IN SCOPE: {target}")
        print(f"    Authorized targets: {len(scope)}")
        
        # Update session state
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            state['last_scope_check'] = {
                'target': target,
                'result': 'PASS',
                'timestamp': datetime.now().isoformat()
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass
        
        sys.exit(0)
    else:
        print(f"[!!!] OUT OF SCOPE: {target}")
        print(f"      This target is NOT in state/scope.txt")
        print(f"      Proceeding would be UNAUTHORIZED.")
        print(f"      Add to scope only if you have written authorization.")
        log_violation(target, "Target not in state/scope.txt")
        sys.exit(1)

if __name__ == '__main__':
    main()
