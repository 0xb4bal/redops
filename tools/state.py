#!/usr/bin/env python3
"""
REDOPS State Manager
Tracks findings, TTPs, submissions across all modes.
Usage: python3 tools/state.py [command] [args]
"""

import json, sys, datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
STATE = BASE / "state" / "session.json"
LOG = BASE / "wiki" / "log.md"

def load():
    with open(STATE) as f: return json.load(f)

def save(s):
    with open(STATE, 'w') as f: json.dump(s, f, indent=2)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    phase = load().get('phase', 'UNKNOWN')
    with open(LOG, 'a') as f:
        f.write(f"\n## [{ts}] {phase.lower()} | {msg}\n")

def status():
    s = load()
    mode = s.get('mode', 'UNSET')
    persona = s.get('persona', 'UNSET')
    findings = s.get('findings', {})
    
    persona_str = (persona or 'UNSET')
    print(f"""
╔══════════════════════════════════════════╗
║         REDOPS STATE — {persona_str:<16}  ║
╚══════════════════════════════════════════╝
  Mode:      {mode}
  Session:   {s.get('session_id', 'None')}
  Target:    {s.get('active_target', 'None')}
  Phase:     {s.get('phase', 'IDLE')}
  Iteration: {s.get('iteration', 0)}
  
  Findings:
    Ports:   {len(findings.get('open_ports', []))}
    Subdom:  {len(findings.get('subdomains', []))}
    Creds:   {len(findings.get('credentials', []))}
    Vulns:   {len(findings.get('vulnerabilities', []))}
    TTPs:    {len(findings.get('ttps_executed', []))}
  
  Bounty:
    Program: {s.get('bug_bounty', {}).get('program', 'N/A')}
    Submits: {len(s.get('bug_bounty', {}).get('submissions', []))}
    Earned:  ${s.get('bug_bounty', {}).get('total_bounty', 0):,}
""")

def add_vuln(name, service, severity, cvss=None, description=None, remediation=None):
    s = load()
    vuln = {
        'name': name, 'service': service, 'severity': severity,
        'cvss': cvss, 'description': description, 'remediation': remediation,
        'discovered': datetime.datetime.now().isoformat()
    }
    s['findings']['vulnerabilities'].append(vuln)
    save(s)
    log(f"vuln [{severity}]: {name} on {service}")
    print(f"[+] Vulnerability added: {name} [{severity}]")

def add_ttp(ttp_id, name, tactic, result, notes=''):
    s = load()
    ttp = {
        'id': ttp_id, 'name': name, 'tactic': tactic,
        'result': result, 'notes': notes,
        'executed': datetime.datetime.now().isoformat()
    }
    s['findings']['ttps_executed'].append(ttp)
    save(s)
    log(f"TTP {ttp_id} {name} [{result}]")
    print(f"[+] TTP logged: {ttp_id} {name} — {result}")
    
    # Update TTP matrix wiki page
    ttp_matrix = BASE / "wiki" / "ttp-matrix.md"
    if ttp_matrix.exists():
        with open(ttp_matrix, 'a') as f:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            f.write(f"| {tactic} | {name} | {ttp_id} | {result} | {ts} |\n")

def add_subdomain(subdomain, status='alive', technologies=''):
    s = load()
    entry = {'subdomain': subdomain, 'status': status, 'technologies': technologies}
    if entry not in s['findings']['subdomains']:
        s['findings']['subdomains'].append(entry)
        save(s)
    print(f"[+] Subdomain: {subdomain} ({status})")

def add_submission(title, severity, program, url, bounty=0):
    s = load()
    sub = {
        'title': title, 'severity': severity, 'program': program,
        'url': url, 'bounty': bounty, 'status': 'submitted',
        'submitted': datetime.datetime.now().isoformat()
    }
    s['bug_bounty']['submissions'].append(sub)
    if bounty: s['bug_bounty']['total_bounty'] += bounty
    save(s)
    log(f"SUBMISSION: {title} [{severity}] to {program} — ${bounty}")
    print(f"[+] Submission: {title} [{severity}] — ${bounty}")

def set_phase(phase):
    s = load()
    old = s['phase']
    s['phase'] = phase
    s['phases_completed'].append({'phase': old, 'at': datetime.datetime.now().isoformat()})
    save(s)
    log(f"phase: {old} → {phase}")
    print(f"[*] Phase: {old} → {phase}")

def increment():
    s = load()
    s['iteration'] += 1
    save(s)
    return s['iteration']

if __name__ == '__main__':
    cmds = {
        'status': (status, 0),
        'phase': (lambda: set_phase(sys.argv[2]), 1),
        'vuln': (lambda: add_vuln(sys.argv[2], sys.argv[3], sys.argv[4],
                                   sys.argv[5] if len(sys.argv)>5 else None), 3),
        'ttp': (lambda: add_ttp(sys.argv[2], sys.argv[3], sys.argv[4],
                                 sys.argv[5], sys.argv[6] if len(sys.argv)>6 else ''), 5),
        'sub': (lambda: add_submission(sys.argv[2], sys.argv[3], sys.argv[4],
                                        sys.argv[5], int(sys.argv[6]) if len(sys.argv)>6 else 0), 5),
        'subdomain': (lambda: add_subdomain(sys.argv[2]), 1),
        'iter': (lambda: print(f"Iteration: {increment()}"), 0),
        'log': (lambda: log(' '.join(sys.argv[2:])), 1),
    }
    
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print("Commands: status, phase, vuln, ttp, sub, subdomain, iter, log")
        status()
        sys.exit(0)
    
    func, _ = cmds[sys.argv[1]]
    func()
