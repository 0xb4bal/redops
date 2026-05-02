# REDOPS — Professional Offensive Security Agent v2.0

> Three agents. One knowledge base. Claude Code CLI.
> **SPECTRE** (Pentest) · **WRAITH** (Red Team) · **HUNTER** (Bug Bounty)

```
┌─────────────────────────────────────────────────────────────────┐
│                      REDOPS AGENT                               │
│                                                                 │
│   SPECTRE          WRAITH           HUNTER                      │
│   ───────          ──────           ──────                      │
│   PTES method      MITRE ATT&CK     OWASP Top 10               │
│   Report-driven    Stealth-first    PoC-driven                  │
│   Scope-bound      ROE-bound        Program-bound               │
│                                                                 │
│   ◄─────────────── wiki/ compounds ──────────────────►          │
│   Techniques learned on one engagement → available on next      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture

| Source | What We Took |
|--------|-------------|
| [autoresearch](https://github.com/karpathy/autoresearch) | Recursive observe→hypothesize→execute loop, `program.md` schema pattern |
| [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | Three-layer persistent knowledge base (raw → wiki → schema), index+log pattern |
| [caveman](https://github.com/JuliusBrussee/caveman) | Token-efficient output — facts only, no filler |
| PTES | Pentest methodology |
| MITRE ATT&CK | Red team TTP tracking |
| OWASP | Bug bounty vuln taxonomy |

---

## Quick Start

### Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### Set up an engagement
```bash
git clone https://github.com/0xb4bal/redops.git
cd redops
chmod +x tools/*.sh tools/*.py

./tools/setup.sh pentest     # corporate pentest
./tools/setup.sh redteam     # adversary simulation
./tools/setup.sh bugbounty   # bug bounty hunting
```

### Start Claude Code
```bash
claude
```

### First prompt
```
Read CLAUDE.md and start /pentest on 10.10.10.5
```
or
```
Read CLAUDE.md. I'm doing bug bounty on hackerone.com/programs/target. 
Start /bugbounty HUNTER mode.
```

---

## Modes

### SPECTRE — Pentester

For: Corporate penetration tests with written scope agreement.

```bash
./tools/setup.sh pentest
claude
# → "Read CLAUDE.md and run /pentest on [TARGET]"
```

Methodology: PTES (Pre-engagement → Recon → Scanning → Enum → Vuln Analysis → Exploit → Post-Exploit → Report)

Output: `wiki/reports/pentest_report_[DATE].md`

### WRAITH — Red Teamer

For: Full-scope adversary simulation with signed ROE.

```bash
./tools/setup.sh redteam
# Copy playbooks/roe-template.md → fill it out → save as state/roe.txt
claude
# → "Read CLAUDE.md and start /redteam WRAITH mode"
```

Methodology: MITRE ATT&CK (Initial Access → Execution → Persistence → Privesc → Defense Evasion → Lateral Movement → Collection → Exfil)

Output: `wiki/reports/redteam_report_[DATE].md` + `wiki/ttp-matrix.md`

### HUNTER — Bug Bounty

For: Bug bounty programs on HackerOne, Bugcrowd, Intigriti, etc.

```bash
./tools/setup.sh bugbounty
claude
# → "Read CLAUDE.md. Program: [URL]. Start /bugbounty"
```

Methodology: Asset discovery → Recon → IDOR/Auth/SSRF/XSS/BizLogic → PoC → Report

Output: `wiki/bounties/[SUBMISSION].md` + `wiki/reports/poc_[DATE].md`

---

## Slash Commands

```
/pentest    Switch to SPECTRE — corporate pentesting mode
/redteam    Switch to WRAITH — adversary simulation mode  
/bugbounty  Switch to HUNTER — bug bounty mode
/recon      Run passive + active reconnaissance
/scan       Network scanning phase (pentest)
/web        Web application testing
/exploit    Exploitation phase
/lateral    Lateral movement (red team)
/ttp [ID]   Log specific MITRE ATT&CK TTP
/hunt [bug] Hunt specific bug class (IDOR/XSS/SSRF/SQLi)
/poc        Generate PoC report template
/report     Generate mode-specific professional report
/state      Show current session state
/scope      Show/check scope
/caveman    Toggle token-efficient output
```

---

## File Structure

```
redops/
├── CLAUDE.md                    ← Agent brain (program.md)
├── README.md                    ← This file
│
├── skills/                      ← Claude Code skill files
│   ├── pentest.skill            ← SPECTRE playbook
│   ├── redteam.skill            ← WRAITH playbook  
│   ├── bugbounty.skill          ← HUNTER playbook
│
├── wiki/                        ← Persistent knowledge base
│   ├── index.md                 ← Master catalog
│   ├── log.md                   ← Append-only audit trail
│   ├── ttp-matrix.md            ← MITRE ATT&CK tracker
│   ├── engagements/             ← One page per client
│   ├── findings/                ← One page per vulnerability
│   ├── bounties/                ← Bug bounty submissions
│   ├── techniques/              ← Reusable attack playbooks
│   └── reports/                 ← Generated reports
│
├── playbooks/                   ← Reference templates
│   ├── poc-template.md          ← Bug bounty PoC format
│   └── roe-template.md          ← Red team ROE template
│
├── state/                       ← Agent runtime state
│   ├── session.json             ← Current session data
│   └── scope.txt                ← Authorized targets
│
├── tools/                       ← Helper scripts
│   ├── setup.sh                 ← Engagement initializer
│   ├── scope.py                 ← Scope enforcer (hard stop)
│   ├── state.py                 ← State manager CLI
│   └── report.py                ← Report generator
│
└── raw/                         ← Immutable tool outputs
    └── [session_id]/
        ├── nmap_fast.txt
        ├── gobuster.txt
        └── ...
```

---

## State Tracker

```bash
# Check status
python3 tools/state.py status

# Log a finding
python3 tools/state.py vuln "SQLi" "/login" "Critical" "9.8"

# Log a TTP (red team)
python3 tools/state.py ttp T1566 "Phishing" "Initial Access" "SUCCESS"

# Log a bug bounty submission
python3 tools/state.py sub "IDOR in /api/users" "High" "HackerOne/target" "https://h1.com/reports/123" 2500

# Generate report
python3 tools/report.py pentest
python3 tools/report.py redteam
python3 tools/report.py poc IDOR High "https://target.com/api/v1/users"
```

---

## Scope Enforcement

The scope checker runs before every tool execution. It will hard-stop if the target is not in `state/scope.txt`.

```bash
# Check a target
python3 tools/scope.py 192.168.1.50       # single IP
python3 tools/scope.py target.example.com # domain
python3 tools/scope.py --list             # show all scope

# Add to scope (requires authorization first!)
python3 tools/scope.py --add 10.10.0.0/24
```

---

## Wiki Compounds

Every engagement enriches the knowledge base:

```
Engagement 1: Found LFI → log poison → RCE on Apache 2.4.38
              → wiki/techniques/lfi-log-poison.md created

Engagement 2: Agent sees Apache 2.4.38 in scan
              → reads wiki/techniques/ → tries LFI first
              → finds it again in 2 minutes
```

This is the LLM Wiki pattern: **knowledge accumulates, never re-derived from scratch.**

---

## Legal & Ethics

- **Written authorization required** for pentest and red team
- **Bug bounty program** must list asset as in-scope
- `state/scope.txt` must be populated before any scanning
- All actions logged in `wiki/log.md` — full audit trail
- No data exfiltration — PoC only, sanitize all screenshots
- Remove all persistence/backdoors after engagement
- Never test out-of-scope assets even if reachable

```
╔════════════════════════════════════════╗
║  Unauthorized access is illegal.       ║
║  This tool is for authorized use only. ║
╚════════════════════════════════════════╝
```
