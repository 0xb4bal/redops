# Bug Bounty PoC Template

> Copy this. Fill it out. Submit.
> HUNTER mode — concise, evidence-driven, professional.

---

## [VULNERABILITY TYPE] in [COMPONENT]

**Program:** [HackerOne / Bugcrowd / Intigriti / Direct]  
**Asset:** `https://target.com/affected/path`  
**Severity:** Critical / High / Medium / Low  
**CVSS 3.1:** [Score] ([Vector String])  
**CWE:** [CWE-XXX]  
**Estimated bounty:** $X,XXX–$XX,XXX  

---

## Summary

[2-3 sentences. What, where, impact. No fluff.]

Example: An IDOR vulnerability in the `/api/v2/accounts/{id}/documents` endpoint
allows any authenticated user to view, download, or delete documents belonging to
other accounts by substituting a different account ID in the path.

---

## Impact

**Who is affected:** All authenticated users  
**What data is exposed:** [specific data types]  
**What actions are possible:** [read/write/delete/execute]  
**Business impact:** [data breach / account takeover / financial loss / etc.]

---

## Reproduction Steps

**Prerequisites:**
- Account A (attacker): `attacker@youremail.com`
- Account B (victim): `victim@youremail.com` ← use your own second account

**Steps:**
1. Log in as Account A at `https://target.com/login`
2. Navigate to `https://target.com/documents/YOUR_DOC_ID`
3. Open Burp Suite → intercept the GET request
4. Change the document ID from `YOUR_DOC_ID` to `VICTIM_DOC_ID`
5. Forward the request
6. **Observe:** Response returns Account B's document content

---

## Proof of Concept

### Request
```http
GET /api/v2/accounts/VICTIM_ACCOUNT_ID/documents/VICTIM_DOC_ID HTTP/1.1
Host: target.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...[ATTACKER TOKEN]
```

### Response (200 OK)
```json
{
  "id": "VICTIM_DOC_ID",
  "owner_id": "VICTIM_ACCOUNT_ID", 
  "content": "sensitive document content",
  "created_at": "2024-01-15"
}
```

### Evidence
- [ ] Screenshot 1: Request with modified ID (blur real victim data)
- [ ] Screenshot 2: Response showing unauthorized access  
- [ ] Video PoC: [optional, strongly recommended for high/critical]

---

## Root Cause Analysis

The application performs authentication (verifies the user is logged in) but
does not perform authorization (does not verify the user owns the requested
resource). Missing authorization check in the document retrieval endpoint.

---

## Remediation

**Short-term:** Add server-side authorization check:
```python
# Before returning document:
if document.owner_id != request.user.id:
    return 403 Forbidden
```

**Long-term:**
- Implement centralized authorization middleware
- Use indirect references (map user-visible IDs to UUIDs internally)
- Add automated IDOR test cases in CI/CD pipeline

---

## Additional Notes

- **Tested on:** [browser/tool]
- **Environment:** Production
- **Rate of exploitation:** Trivial (no special tools required)
- **Authentication required:** Yes (valid account)
- **Data accessed during testing:** Only my own test accounts
- **Data stored/downloaded:** None

---

## Timeline

| Date/Time | Event |
|-----------|-------|
| YYYY-MM-DD HH:MM | Vulnerability discovered during normal testing |
| YYYY-MM-DD HH:MM | Vulnerability confirmed (tested 3x) |
| YYYY-MM-DD HH:MM | Report drafted |
| YYYY-MM-DD HH:MM | Report submitted |

---

## Similar/Related Reports

[If you found related issues, document separately but reference here]

---

*Filed: wiki/bounties/[PROGRAM]_[DATE]_[VULN_TYPE].md*
