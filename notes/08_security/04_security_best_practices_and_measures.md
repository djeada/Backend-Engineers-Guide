## Security Best Practices and Measures

Security is a multi-layered concern involving networks, systems, applications, data, users, and operational processes. A single misconfiguration, weak password, missing patch, exposed secret, or insecure dependency can give attackers a path into a system.

Good security is built through **defense in depth**. This means using multiple layers of protection so that if one control fails, another control can still reduce the damage. Firewalls, secure coding, encryption, access control, monitoring, patching, backups, and incident response all work together.

Security should also be treated as an ongoing process. Systems change, dependencies age, attackers adapt, and new vulnerabilities are discovered. Best practices must be reviewed, tested, and improved over time.

### Network Security

Network security protects communication paths, servers, databases, and internal systems from unauthorized access. It controls which systems can talk to each other and which traffic is allowed into or out of the environment.

A secure network design reduces the attack surface. Public-facing systems should be separated from sensitive internal systems, and access should be restricted by default.

#### Segregate and Secure Network Zones

An important principle is to separate public-facing services from sensitive backend systems. For example, web servers may sit in a DMZ, while databases remain in a private internal network.

A DMZ, or demilitarized zone, is a network area exposed to controlled inbound traffic. It allows public services to be reachable without exposing the entire internal network.

```text id="ow8kw3"
      Internet
          |
          | Inbound Traffic
          v
   +---------------+       +------------------+
   |    Firewall   |------>|   DMZ Network    |
   | Edge Device   |       |   Web Servers    |
   +---------------+       +--------+---------+
                                    |
                                    | Restricted
                                    v
                           +--------------------+
                           | Internal Network   |
                           | DB Servers, etc.   |
                           +--------------------+
```

Example firewall policy:

```text id="hvpmtm"
Allow Internet → Web Servers on TCP 443
Allow Web Servers → Database on TCP 5432
Deny Internet → Database
Deny all other inbound traffic by default
```

Example output:

```json id="zdhppd"
{
  "internetToWeb": "allowed",
  "internetToDatabase": "blocked",
  "webToDatabase": "allowed",
  "defaultPolicy": "deny"
}
```

Firewalls should allow only necessary ports and protocols. A web server may need HTTPS from the internet, but the database should usually accept connections only from application servers.

Zero Trust and micro-segmentation extend this idea further. Instead of assuming internal traffic is safe, every connection is authenticated, authorized, and monitored.

#### Use Secure Protocols

Insecure protocols should be disabled. Older protocols may send credentials or data in plaintext, making them vulnerable to interception.

Avoid protocols such as Telnet, plain FTP, and old SSL versions. Prefer SSH, SFTP, HTTPS, and modern TLS.

Example SSH hardening configuration:

```bash id="hrf14s"
# /etc/ssh/sshd_config

Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers user1 user2
```

Example command to apply changes:

```bash id="i0vi76"
sudo systemctl restart sshd
```

Example expected result:

```json id="ne4xt2"
{
  "rootLogin": "disabled",
  "passwordLogin": "disabled",
  "publicKeyLogin": "enabled",
  "allowedUsers": ["user1", "user2"]
}
```

Disabling password-based SSH reduces the risk of brute-force login attacks. Restricting allowed users reduces the number of accounts attackers can target.

#### Intrusion Detection and Prevention Systems

Intrusion Detection Systems, or IDS, monitor traffic and alert on suspicious patterns. Intrusion Prevention Systems, or IPS, can actively block or drop traffic that appears malicious.

Tools such as Snort and Suricata can inspect packets, detect known attack signatures, and identify unusual network behavior.

Example IDS alert:

```json id="8n2bcs"
{
  "alert": "Possible SQL injection attempt",
  "sourceIp": "203.0.113.50",
  "destination": "web-server-1",
  "severity": "high"
}
```

IDS and IPS tools are not replacements for secure application design, but they provide another detection layer. They are useful for spotting attacks that bypass basic firewall rules.

### Application Security

Application security focuses on preventing vulnerabilities in the software itself. Since applications process user input, enforce business rules, and access databases, insecure code can create serious risks.

Common application vulnerabilities include injection attacks, cross-site scripting, broken access control, insecure session handling, unsafe file uploads, and insecure deserialization.

#### Secure Coding Practices

Secure coding starts with treating all external input as untrusted. User input, headers, cookies, uploaded files, API payloads, query parameters, and third-party webhook data should all be validated before use.

Important practices include:

* **Input Validation**: Check type, length, format, and allowed values.
* **Parameterized Queries**: Prevent SQL injection by separating query logic from user input.
* **Output Encoding**: Prevent XSS by safely encoding data before rendering it into HTML, JavaScript, or URLs.
* **Safe Error Handling**: Return generic errors to users while logging detailed errors internally.

Example safe SQL query in Python:

```python id="hp7mbl"
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (user_input,)
)
```

Unsafe string concatenation:

```python id="9iat67"
cursor.execute(
    "SELECT * FROM users WHERE username = '" + user_input + "'"
)
```

Example malicious input:

```text id="3o8xqb"
' OR '1'='1
```

Example safe output:

```json id="roa89o"
{
  "status": "rejected",
  "reason": "input treated as data, not executable SQL"
}
```

Parameterized queries prevent user input from changing the structure of the SQL command.

#### Secure Session Management

Sessions identify users across requests. If session handling is weak, attackers may hijack accounts or impersonate users.

Session cookies should be protected with secure attributes:

```http id="zbsuv8"
Set-Cookie: SESSION_ID=abc123456; HttpOnly; Secure; SameSite=Strict
```

These attributes help protect the cookie:

* `HttpOnly` prevents JavaScript from reading the cookie.
* `Secure` sends the cookie only over HTTPS.
* `SameSite=Strict` reduces cross-site request risks.

Example session security output:

```json id="7mjgzn"
{
  "httpOnly": true,
  "secure": true,
  "sameSite": "Strict",
  "sessionRotation": "enabled"
}
```

Session tokens should be random, long enough, and rotated after login or privilege changes. Sensitive applications should use short idle timeouts and require re-authentication for high-risk actions.

#### Content Security Policies

Content Security Policy, or CSP, restricts which sources can load scripts, images, frames, styles, and other resources. It is especially useful for reducing the impact of cross-site scripting attacks.

Example Nginx CSP header:

```nginx id="jy7350"
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; object-src 'none';";
```

Example policy effect:

```json id="w4gq8l"
{
  "defaultSource": "self",
  "externalScripts": "blocked",
  "plugins": "blocked"
}
```

If an attacker injects a script from an unapproved domain, the browser can block it. CSP should be tested carefully because strict policies can break legitimate resources if they are not included.

### Data Security

Data security protects information from unauthorized access, modification, or disclosure. It includes encryption, access control, retention policies, backups, masking, and safe handling of sensitive records.

Sensitive data may include passwords, personal information, payment details, health information, business secrets, private messages, tokens, and credentials.

#### Encryption at Rest

Encryption at rest protects stored data. This includes databases, disk volumes, backups, object storage, and file systems.

If an attacker gains access to raw storage, encryption helps prevent them from reading the data without the key.

Examples include:

* Database-level encryption.
* Disk encryption such as LUKS.
* Cloud-managed storage encryption.
* Application-level encryption for especially sensitive fields.

Example encrypted storage status:

```json id="pne7az"
{
  "databaseEncryption": "enabled",
  "backupEncryption": "enabled",
  "diskEncryption": "enabled"
}
```

Passwords should not be encrypted for later recovery. They should be hashed with a strong password-hashing algorithm such as Argon2, bcrypt, or PBKDF2.

#### Encryption in Transit

Encryption in transit protects data while it moves over a network. TLS should be used for client-server communication and, where possible, internal service-to-service communication.

```text id="8sr6se"
+------------------+     TLS/HTTPS     +---------------------+
|  Client Browser  | <---------------> |  Web Server HTTPS   |
+------------------+                   +---------------------+
```

Example HTTPS response:

```http id="cue9a9"
HTTP/1.1 200 OK
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Example output:

```json id="fzh4qn"
{
  "tls": "enabled",
  "hsts": "enabled",
  "weakProtocols": "disabled"
}
```

Servers should prefer TLS 1.2 or TLS 1.3 and disable SSLv2, SSLv3, TLS 1.0, and TLS 1.1 unless there is a strict legacy requirement.

#### Key Management

Encryption is only as secure as the keys protecting it. Private keys, signing keys, database encryption keys, and API secrets should be stored and managed carefully.

Good key management includes:

* Storing keys in secure systems such as KMS, HSMs, or secrets managers.
* Restricting access to keys.
* Rotating keys periodically.
* Revoking keys if compromised.
* Auditing key usage.

Example key access log:

```json id="8z2t30"
{
  "principal": "payment-service",
  "key": "prod/payment-encryption-key",
  "action": "decrypt",
  "result": "allowed",
  "timestamp": "2026-04-25T12:00:00Z"
}
```

Keys should not be hardcoded in source code, stored in public repositories, printed in logs, or embedded into container images.

### Access Control

Access control determines who or what is allowed to access resources. This includes users, services, applications, administrators, CI/CD systems, and third-party integrations.

Access control should be enforced on the server side. Frontend checks can improve user experience, but they cannot protect data by themselves.

#### Principle of Least Privilege

The Principle of Least Privilege means every user, service, or process should receive only the permissions needed to perform its job.

Examples:

* A reporting database user gets read-only access.
* A web application account can access only the required schema.
* A service account can read only the secrets it needs.
* An administrator uses elevated privileges only when needed.

Example permission model:

```json id="3833te"
{
  "service": "reporting-service",
  "databasePermissions": ["SELECT"],
  "writeAccess": false,
  "adminAccess": false
}
```

Least privilege limits damage if an account, token, or service is compromised.

#### Role-Based Access Control

Role-Based Access Control, or RBAC, assigns permissions to roles and then assigns users to those roles. This makes access easier to manage as people join, change teams, or leave.

Example PostgreSQL RBAC:

```sql id="y2315x"
-- Create a read-only role
CREATE ROLE read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;

-- Assign user to read_only role
CREATE USER reporter WITH PASSWORD 'secret';
GRANT read_only TO reporter;
```

Example access result:

```json id="k6wkpk"
{
  "user": "reporter",
  "role": "read_only",
  "canSelect": true,
  "canUpdate": false,
  "canDelete": false
}
```

RBAC reduces the need to manage permissions one user at a time. For more complex systems, attribute-based access control may also be used.

#### Multi-Factor Authentication

Multi-factor authentication, or MFA, requires users to provide more than one proof of identity. For example, a password plus a TOTP code, push approval, or hardware security key.

MFA reduces the risk of account takeover if a password is stolen.

Example login flow:

```text id="4ni4se"
User enters password.
System verifies password.
System requests second factor.
User provides TOTP or hardware key confirmation.
Access is granted.
```

Example output:

```json id="cugyqu"
{
  "passwordValid": true,
  "mfaRequired": true,
  "mfaVerified": true,
  "loginStatus": "success"
}
```

MFA should be required for administrators, production access, cloud consoles, CI/CD systems, and sensitive business applications.

### Monitoring and Logging

Monitoring and logging help teams detect attacks, investigate incidents, and understand system behavior. Without logs, it is difficult to know what happened during a security event.

Good logging should capture important events without exposing sensitive data. Logs should be centralized, protected, searchable, and retained according to policy.

#### Centralized Log Collection

Centralized log collection aggregates logs from many systems into one platform. This makes it easier to correlate events across web servers, databases, firewalls, identity systems, and applications.

```text id="xiqzuh"
+----------------+  +----------------+   +-----------------+
| Web Servers    |  | DB Servers     |   | Firewalls/IDPS  |
| logs           |  | logs           |   | logs            |
+--------+-------+  +--------+-------+   +--------+--------+
         |                  |                     |
         | Syslog/Beat      | Syslog/Beat         |
         v                  v                     v
       +-------------------------------+
       |    Central Log Collector      |
       | Elasticsearch, Splunk, etc.   |
       +-------------------------------+
```

Example centralized log entry:

```json id="pwy1jo"
{
  "timestamp": "2026-04-25T12:00:00Z",
  "service": "auth-api",
  "event": "failed_login",
  "user": "alice@example.com",
  "sourceIp": "203.0.113.50"
}
```

Centralized logs help identify patterns that may not be obvious from one server alone.

#### Alerting and Anomaly Detection

Alerts notify teams when suspicious or abnormal behavior occurs. This may include large data exports, unusual login locations, repeated failed logins, sudden traffic spikes, high error rates, or access outside normal hours.

Example alert rule:

```text id="00wpx2"
Trigger alert if:
failed_login_count > 20 for same user within 5 minutes
```

Example alert output:

```json id="794spg"
{
  "alert": "Possible brute-force attack",
  "user": "alice@example.com",
  "failedAttempts": 28,
  "timeWindow": "5 minutes",
  "severity": "high"
}
```

Anomaly detection can also compare behavior against baselines. For example, a user downloading 10 GB of data at 3 AM may be unusual if they normally access only a few records during business hours.

#### Audit Trails

Audit trails record important user and system actions. They are especially important for administrative actions, financial changes, permission updates, data exports, and security-sensitive operations.

A good audit log includes timestamp, user identity, source IP, action, resource, result, and any changed values.

Example audit entry:

```json id="r9lek7"
{
  "timestamp": "2026-04-25T12:05:00Z",
  "actor": "admin-123",
  "action": "grant_role",
  "targetUser": "user-456",
  "role": "billing_admin",
  "sourceIp": "198.51.100.20",
  "result": "success"
}
```

Audit logs should be protected from tampering. Append-only storage, restricted permissions, and cryptographic integrity checks can help preserve trust in the records.

### Patch Management and Hardening

Patch management and hardening reduce the number of known weaknesses in systems. Attackers often exploit vulnerabilities that already have public fixes, so staying current is one of the most effective defenses.

#### Regular Updates

Operating systems, applications, libraries, containers, and firmware should be kept up to date. Teams should subscribe to vendor security advisories and use automated patch management where possible.

Example Ubuntu update:

```bash id="2k9qci"
sudo apt-get update
sudo apt-get upgrade
```

Example output:

```text id="6wf66t"
15 packages upgraded
0 newly installed
Security updates applied successfully
```

Patches should be tested before production rollout when possible, especially for critical systems. Emergency security patches may require faster deployment.

#### System Hardening

System hardening removes unnecessary services, closes unused ports, disables default accounts, restricts permissions, and applies secure configuration baselines.

Example firewall rules:

```bash id="oew4xs"
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

Example result:

```json id="r1w6bh"
{
  "allowedInboundPorts": [22, 443],
  "defaultInboundPolicy": "drop"
}
```

This allows SSH and HTTPS while dropping other inbound traffic. In production, SSH may be further restricted to a VPN, bastion host, or trusted IP range.

Tools such as CIS Benchmarks, OpenSCAP, and cloud security posture tools can guide hardening work.

#### Secure Configuration Baselines

Secure baselines define standard settings for servers, containers, cloud accounts, databases, and network devices. They make security consistent across environments.

Automation tools such as Ansible, Chef, Puppet, Terraform, and cloud policy engines can enforce these baselines.

Example baseline output:

```json id="am26sl"
{
  "sshRootLogin": "disabled",
  "firewall": "enabled",
  "diskEncryption": "enabled",
  "auditLogging": "enabled",
  "automaticSecurityUpdates": "enabled"
}
```

Automated checks help ensure new systems are created securely instead of relying on manual configuration.

### Incident Response and Recovery

Even strong security programs must assume incidents can happen. Incident response prepares teams to detect, contain, investigate, eradicate, recover, and learn from security events.

A good response plan reduces confusion during a crisis. It defines roles, responsibilities, communication paths, and technical steps.

#### Prepare an Incident Response Plan

An incident response plan should explain how the organization handles security incidents. It should identify key roles such as Incident Commander, Communications Lead, Forensics Lead, Legal Contact, and Engineering Lead.

Example incident response structure:

```json id="6hpktb"
{
  "incidentCommander": "security-lead",
  "communicationsLead": "comms-lead",
  "forensicsLead": "infra-security",
  "legalContact": "legal-team",
  "severity": "high"
}
```

The plan should include escalation paths, emergency contacts, evidence handling procedures, and criteria for notifying customers, regulators, or law enforcement.

#### Backups and Recovery

Backups protect against ransomware, accidental deletion, corruption, and catastrophic failures. Backups should be automated, encrypted, access-controlled, and stored separately from production systems.

Offline or immutable backups are especially useful against ransomware because attackers cannot easily modify or delete them.

Example backup policy:

```json id="d8fhbg"
{
  "frequency": "daily",
  "storage": "offsite",
  "encryption": "enabled",
  "retentionDays": 30,
  "restoreTests": "monthly"
}
```

Backups must be tested. A backup that cannot be restored is not useful.

Example restore test output:

```json id="q9g3kz"
{
  "backupDate": "2026-04-25",
  "restoreStatus": "success",
  "recordsVerified": 250000
}
```

#### Post-Incident Review

After an incident is resolved, teams should perform a post-incident review. The goal is not blame. The goal is to understand what happened, why it happened, and how to prevent a similar issue.

A useful review should identify root causes, detection gaps, response delays, missing controls, and follow-up actions.

Example post-incident output:

```json id="0lzj2r"
{
  "rootCause": "unpatched dependency",
  "detectionGap": "no alert for unusual outbound traffic",
  "correctiveActions": [
    "enable dependency scanning",
    "add egress monitoring",
    "rotate affected credentials",
    "update patch SLA"
  ]
}
```

Post-incident learning turns security failures into stronger defenses.

### Additional Best Practices

Security should be integrated into everyday engineering and operations.

#### Security by Design

Security should be considered during system design, not added only after deployment. Threat modeling, secure architecture reviews, and least-privilege design can prevent problems before code is written.

Example design review result:

```json id="m610t1"
{
  "publicDatabaseAccess": "removed",
  "serviceAuthentication": "required",
  "sensitiveDataFlow": "documented"
}
```

#### Regular Security Assessments

Run vulnerability scans, penetration tests, dependency scans, infrastructure reviews, and code reviews. These assessments help find weaknesses before attackers exploit them.

Example scan output:

```json id="dwp2qw"
{
  "criticalFindings": 0,
  "highFindings": 2,
  "mediumFindings": 7,
  "status": "remediation_required"
}
```

#### Employee Training

People are part of the security system. Train staff to recognize phishing, social engineering, suspicious links, unsafe credential sharing, and risky data handling.

Example training result:

```json id="d6rc04"
{
  "training": "phishing awareness",
  "completionRate": "96%",
  "reportedPhishingAttempts": 42
}
```

#### Rotate Credentials

Admin passwords, API tokens, SSH keys, encryption keys, and service credentials should be rotated periodically and immediately after suspected exposure.

Example rotation output:

```json id="e84fga"
{
  "credential": "production-api-key",
  "rotationStatus": "completed",
  "oldCredentialRevoked": true
}
```

#### Use Reputable Libraries

Third-party libraries should be reviewed before adoption. Avoid abandoned, unmaintained, or unnecessary dependencies. Use dependency scanning and lock files to reduce supply chain risk.

Example dependency review:

```json id="7jikmd"
{
  "package": "example-lib",
  "maintained": true,
  "knownVulnerabilities": 0,
  "approved": true
}
```

#### Carry Out Honeytokens and Honeypots

Honeytokens are fake credentials, records, or resources designed to detect unauthorized access. Honeypots are decoy systems that attract attackers and reveal malicious behavior.

Example honeytoken alert:

```json id="2j7mg0"
{
  "alert": "Honeytoken used",
  "token": "fake-prod-api-key",
  "sourceIp": "203.0.113.50",
  "severity": "critical"
}
```

If a honeytoken is used, it likely means someone accessed a location they should not have accessed.
