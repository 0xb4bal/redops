# Rules of Engagement (ROE)

> WRAITH / Red Team Mode — REQUIRED before any operation.
> Fill this out with client before engagement starts.
> Store signed copy here. Reference throughout engagement.

---

## Engagement Details

| Field | Value |
|-------|-------|
| Client | [Company Name] |
| Engagement | [Name/ID] |
| Start Date | YYYY-MM-DD |
| End Date | YYYY-MM-DD |
| Authorized By | [Name, Title] |
| Emergency Contact | [Name, Phone] |
| Red Team Lead | [Name] |
| Blue Team Contact | [Name — for deconfliction] |

---

## Scope

### In Scope

**Networks:**
- [ ] Internal network: [CIDR]
- [ ] DMZ: [CIDR]
- [ ] Cloud: [AWS account / Azure sub]

**Systems:**
- [ ] All workstations
- [ ] All servers (list exclusions below)
- [ ] Domain controllers
- [ ] Cloud instances

**Attack Vectors:**
- [ ] External reconnaissance (OSINT)
- [ ] Phishing (email)
- [ ] Phishing (phone/vishing)
- [ ] Physical (badge cloning, tailgating)
- [ ] External service exploitation
- [ ] Wireless attacks
- [ ] Insider threat simulation

---

### Out of Scope (NEVER TEST)

- [ ] Production databases with real customer PII
- [ ] Payment processing systems (specify: ________________)
- [ ] Life-safety systems
- [ ] Third-party systems not owned by client
- [ ] Specific hosts: ________________

---

## Permitted Actions

| Action | Permitted | Notes |
|--------|-----------|-------|
| Port scanning | ✓/✗ | |
| Vulnerability scanning | ✓/✗ | |
| Password spraying | ✓/✗ | Max: N attempts per account per hour |
| Phishing (simulated) | ✓/✗ | Max N emails, no malware links |
| Exploitation | ✓/✗ | No destructive payloads |
| Data exfil (simulated) | ✓/✗ | Dummy data only |
| Persistence | ✓/✗ | Remove all within N days |
| Lateral movement | ✓/✗ | Notify deconfliction before pivot |
| Denial of service | ✗ | NEVER |
| Ransomware simulation | ✓/✗ | Isolated test systems only |

---

## Deconfliction Protocol

**Before pivoting to new host:**
```bash
python3 tools/deconflict.py --notify "Moving to $NEW_HOST from $CURRENT_HOST"
```

**Blue team contact:** [Name] [Phone] [Email]
**Deconfliction window:** [How quickly blue team will respond — e.g., 15min]
**If no response:** [Pause operation / proceed with caution]

---

## Emergency Halt Conditions

STOP IMMEDIATELY and contact client if:
1. Real ransomware/destructive malware discovered on network
2. Evidence of active third-party attacker on network
3. Out-of-scope system accidentally accessed
4. Any indication real data has been exfiltrated
5. Blue team escalates to IR mode

**Kill switch:** Contact [Name] at [Phone] anytime.

---

## Rules

1. **No data exfil** — Demonstrate capability, do not move real data
2. **No destructive payloads** — Reverse shells OK, not wipers/lockers
3. **No out-of-scope** — Even if you CAN reach it, don't
4. **Log everything** — wiki/log.md is your friend
5. **Deconflict before lateral** — Call blue team before pivoting
6. **Clean up** — Remove all persistence, backdoors, dropped files within 48h of engagement end
7. **No attribution disclosure** — Don't reveal red team existence to employees under test

---

## Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Client CISO | | | |
| Client Legal | | | |
| Red Team Lead | | | |

---

*File this signed document before engagement starts.*
*Reference: state/roe.txt must exist for WRAITH mode to activate.*
