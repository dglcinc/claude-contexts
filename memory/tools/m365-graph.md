---
name: Microsoft 365 — outbound email via Graph instead of SMTP
description: Modern M365 tenants disable SMTP AUTH; use MSAL + Graph sendMail
type: tools
---

# Microsoft 365 — outbound email

## SMTP AUTH is dead in modern tenants

Microsoft has been disabling SMTP AUTH (`smtp.office365.com:587`) tenant-wide since 2022; new tenants ship with it off. Don't reach for SMTP creds for service-to-service mail — they probably won't work, and if they do today they'll stop working soon.

**Use Microsoft Graph `sendMail` with the client-credentials OAuth2 flow** instead. Same Azure AD app can serve any number of services that need to send mail.

## Recipe (Python stdlib only)

```python
import json, os, urllib.parse, urllib.request

def graph_token(tenant_id, client_id, client_secret):
    data = urllib.parse.urlencode({
        'grant_type':    'client_credentials',
        'client_id':     client_id,
        'client_secret': client_secret,
        'scope':         'https://graph.microsoft.com/.default',
    }).encode()
    req = urllib.request.Request(
        f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
        data=data, method='POST')
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())['access_token']

def send_mail(sender, recipient, subject, html_body, tenant_id, client_id, client_secret):
    token = graph_token(tenant_id, client_id, client_secret)
    payload = json.dumps({
        'message': {
            'subject': subject,
            'body':    {'contentType': 'HTML', 'content': html_body},
            'toRecipients': [{'emailAddress': {'address': recipient}}],
        },
        'saveToSentItems': True,
    }).encode()
    req = urllib.request.Request(
        f'https://graph.microsoft.com/v1.0/users/{sender}/sendMail',
        data=payload,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST')
    with urllib.request.urlopen(req, timeout=15):
        pass  # 202 Accepted
```

No external deps required. The bowling-league-tracker's `check_health.py` is a working production reference.

## Azure app setup (one-time, per Azure AD app)

1. Azure Portal → App registrations → New registration
2. API permissions → Microsoft Graph → **Application** permission → `Mail.Send`
3. Grant admin consent
4. Certificates & secrets → New client secret → save the value (only shown once)
5. Note tenant ID, application (client) ID, client secret value
6. The `sender` parameter must match a real mailbox in the tenant; the app sends "as" that mailbox

## Reuse pattern

The same `(tenant_id, client_id, client_secret, sender)` tuple can drive any number of services. dglcinc's bowling-league-tracker app is the canonical setup; tools that need to send mail (Grafana alerting bridges, healthchecks, etc.) reuse the same secret. Store the env vars in `/etc/<service>/graph.env` mode 640 root:<service-user>; never check them in.

## Why not SMTP at all?

- Disabled by default in M365.
- Requires per-mailbox password (or app password if MFA), not the elegant per-app secret.
- Can't be revoked surgically — rotating an app password breaks every other consumer of that mailbox.
- Graph is rate-limited per app, not per mailbox; better operational separation.
