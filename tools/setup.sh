#!/bin/bash
# REDOPS Engagement Initializer
# Usage: ./tools/setup.sh [pentest|redteam|bugbounty]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BOLD}${CYAN}"
cat << 'EOF'
 ██████╗ ███████╗██████╗  ██████╗ ██████╗ ███████╗
 ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔════╝
 ██████╔╝█████╗  ██║  ██║██║   ██║██████╔╝███████╗
 ██╔══██╗██╔══╝  ██║  ██║██║   ██║██╔═══╝ ╚════██║
 ██║  ██║███████╗██████╔╝╚██████╔╝██║     ███████║
 ╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚═╝     ╚══════╝
 Professional Offensive Security Agent v2.0
EOF
echo -e "${RESET}"

# ── Mode Selection ─────────────────────────────────────────
if [ -z "$1" ]; then
    echo -e "${BOLD}Select mode:${RESET}"
    echo "  1) pentest   — SPECTRE (corporate pentesting)"
    echo "  2) redteam   — WRAITH  (adversary simulation)"
    echo "  3) bugbounty — HUNTER  (bug bounty hunting)"
    read -p "Mode [1-3]: " MODE_NUM
    case $MODE_NUM in
        1) MODE="pentest"   ;;
        2) MODE="redteam"   ;;
        3) MODE="bugbounty" ;;
        *) echo "Invalid"; exit 1 ;;
    esac
else
    MODE=$1
fi

case $MODE in
    pentest)
        PERSONA="SPECTRE"
        echo -e "${GREEN}[+] Mode: PENTEST — Persona: SPECTRE${RESET}"
        ;;
    redteam)
        PERSONA="WRAITH"
        echo -e "${GREEN}[+] Mode: RED TEAM — Persona: WRAITH${RESET}"
        ;;
    bugbounty)
        PERSONA="HUNTER"
        echo -e "${GREEN}[+] Mode: BUG BOUNTY — Persona: HUNTER${RESET}"
        ;;
    *)
        echo -e "${RED}[!] Invalid mode: $MODE${RESET}"
        exit 1
        ;;
esac

# ── Engagement Info ─────────────────────────────────────────
echo ""
read -p "Engagement/Program name: " ENGAGEMENT_NAME
read -p "Client/Company: " CLIENT

if [ "$MODE" == "bugbounty" ]; then
    read -p "Bug bounty program URL: " PROGRAM_URL
    read -p "Platform (hackerone/bugcrowd/intigriti/other): " PLATFORM
fi

if [ "$MODE" == "pentest" ] || [ "$MODE" == "redteam" ]; then
    read -p "Authorization document reference: " AUTH_REF
    read -p "Engagement start date (YYYY-MM-DD): " START_DATE
    read -p "Engagement end date (YYYY-MM-DD): " END_DATE
fi

# ── Scope Configuration ─────────────────────────────────────
echo ""
echo -e "${YELLOW}[*] Scope Configuration${RESET}"
echo "Enter in-scope targets (one per line). Empty line when done."
echo "Formats: IP, CIDR, IP-range, domain, *.wildcard.com"
echo ""

# Backup existing scope
cp state/scope.txt state/scope.txt.bak 2>/dev/null || true

# Write scope header
TIMESTAMP=$(date '+%Y-%m-%d')
cat > state/scope.txt << SCOPE_HEADER
# REDOPS Scope — $ENGAGEMENT_NAME
# Client: $CLIENT
# Mode: $MODE
# Date: $TIMESTAMP
# NEVER test targets not listed below.
SCOPE_HEADER

echo "" >> state/scope.txt
echo "# === IN-SCOPE TARGETS ===" >> state/scope.txt

TARGET_COUNT=0
while true; do
    read -p "  Target (or Enter to finish): " SCOPE_ENTRY
    [ -z "$SCOPE_ENTRY" ] && break
    echo "$SCOPE_ENTRY" >> state/scope.txt
    echo -e "  ${GREEN}[✓] Added: $SCOPE_ENTRY${RESET}"
    TARGET_COUNT=$((TARGET_COUNT + 1))
done

echo ""
if [ "$TARGET_COUNT" -eq 0 ]; then
    echo -e "${RED}[!] No targets added. Scope is empty.${RESET}"
    echo "    Add targets to state/scope.txt before scanning."
fi

# ── Primary Target ───────────────────────────────────────────
read -p "Primary target for this session (IP or domain): " PRIMARY_TARGET

# Scope check
echo ""
echo -e "${YELLOW}[*] Scope verification...${RESET}"
if python3 tools/scope.py "$PRIMARY_TARGET" 2>&1; then
    echo -e "${GREEN}[✓] Target verified in scope${RESET}"
else
    echo -e "${RED}[!!!] Target not in scope. Add to state/scope.txt first.${RESET}"
    exit 1
fi

# ── VPN Check (for pentest/redteam) ─────────────────────────
if [ "$MODE" != "bugbounty" ]; then
    echo ""
    echo -e "${YELLOW}[*] VPN check...${RESET}"
    if ip a show tun0 &>/dev/null 2>&1; then
        VPN_IP=$(ip a show tun0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 2>/dev/null)
        echo -e "${GREEN}[✓] VPN connected: tun0 = $VPN_IP${RESET}"
        export ATTACKER_IP=$VPN_IP
    else
        echo -e "${YELLOW}[!] tun0 not found. Ensure VPN is connected for internal engagements.${RESET}"
        read -p "Your attack machine IP: " ATTACKER_IP
        export ATTACKER_IP
    fi
fi

# ── Session ID ───────────────────────────────────────────────
SESSION_ID="${MODE}_$(echo $ENGAGEMENT_NAME | tr ' ' '_' | tr '[:upper:]' '[:lower:]')_$(date +%Y%m%d_%H%M%S)"
export SESSION_ID MODE PERSONA PRIMARY_TARGET

mkdir -p raw/$SESSION_ID

# ── Wiki Pages ───────────────────────────────────────────────
WIKI_DIR="wiki/engagements"
mkdir -p $WIKI_DIR wiki/findings wiki/bounties

# Create engagement page
cat > "$WIKI_DIR/${SESSION_ID}.md" << WIKI_PAGE
# Engagement: $ENGAGEMENT_NAME

> Mode: $MODE | Persona: $PERSONA
> Client: $CLIENT
> Session: $SESSION_ID
> Date: $TIMESTAMP
> Primary Target: $PRIMARY_TARGET

## Scope

$(cat state/scope.txt | grep -v '^#' | grep -v '^$' | sed 's/^/- /')

## Objectives

- [ ] Define (based on engagement type)

## Timeline

- $TIMESTAMP — Session initialized

## Findings Summary

_None yet_

## Key Notes

_None yet_
WIKI_PAGE

echo -e "${GREEN}[✓] Created: wiki/engagements/${SESSION_ID}.md${RESET}"

# ── Log Entry ────────────────────────────────────────────────
LOGTS=$(date '+%Y-%m-%d %H:%M')
cat >> wiki/log.md << LOG_ENTRY

## [$LOGTS] init | Session started: $ENGAGEMENT_NAME ($MODE/$PERSONA)
Target: $PRIMARY_TARGET | Session: $SESSION_ID
LOG_ENTRY

# ── State Update ─────────────────────────────────────────────
python3 - << PYEOF
import json, datetime

with open('state/session.json') as f:
    state = json.load(f)

state.update({
    'mode': '$MODE',
    'persona': '$PERSONA',
    'session_id': '$SESSION_ID',
    'phase': 'RECON',
    'iteration': 1,
    'active_target': '$PRIMARY_TARGET',
    'engagement': {
        'name': '$ENGAGEMENT_NAME',
        'type': '$MODE',
        'client': '$CLIENT',
        'start_date': '$TIMESTAMP',
        'authorization': '${AUTH_REF:-N/A (Bug Bounty)}'
    }
})

with open('state/session.json', 'w') as f:
    json.dump(state, f, indent=2)

print('[✓] state/session.json updated')
PYEOF

# ── Final Summary ─────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}=== Session Ready ===${RESET}"
echo ""
echo -e "  Mode:     ${CYAN}$MODE${RESET} (${PERSONA})"
echo -e "  Target:   ${CYAN}$PRIMARY_TARGET${RESET}"
echo -e "  Session:  ${CYAN}$SESSION_ID${RESET}"
echo -e "  Scope:    ${CYAN}$TARGET_COUNT targets${RESET}"
echo ""
echo -e "${BOLD}Start Claude Code:${RESET}"
echo "  claude"
echo ""
echo -e "${BOLD}First prompt:${RESET}"
echo "  \"Read CLAUDE.md and start /$MODE on $PRIMARY_TARGET\""
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${YELLOW} Reminder: Only test authorized targets.${RESET}"
echo -e "${YELLOW} All actions are logged in wiki/log.md${RESET}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
