Review the changes on @branch:

## General Review

– Think through how data flows in the app. Explain new patterns if they exist and why.
– Were there any changes that could affect infrastructure?
– Consider empty, loading, error, and offline states.
– Review frontend changes for a11y (keyboard navigation, focus management, ARIA roles, color contrast).
– If public APIs have changed, ensure backwards compat (or increment API version).
– Did we add any unnecessary dependencies? If there's a heavy dependency, could we inline a more minimal version?
– Did we add quality tests? Prefer fewer, high quality tests. Prefer integration tests for user flows.
– Were there schema changes which could require a database migration?
– If feature flags are set up, does this change require adding a new one?
– If i18n is set up, are the strings added localized and new routes internationalized?
– Are there places we should use caching?
– Are we missing critical o11y or logging on backend changes?

## Security Review

- Auth & Sessions: verify login flows, token lifetimes, refresh logic, cookie flags (`Secure`, `HttpOnly`, `SameSite`), and logout invalidation.
- Authorization: confirm role/permission checks exist on every privileged path; no new endpoints bypass policy.
- Data Exposure: audit API responses, logs, errors for secrets, PII, or internal IDs; ensure redaction/encryption where required.
- Input Handling: inspect user-controlled inputs for injection (SQL/NoSQL, command, template), XSS, CSRF tokens, SSRF, path traversal.
- Dependencies: note new packages; check for supply-chain risk, sandboxing, or native bindings that expand the attack surface.
- Transport & Storage: ensure TLS requirements, certificate pinning (if applicable), and at-rest encryption or key management updates.
- Infrastructure & Secrets: look for new env vars, config files, or cloud resources; confirm secrets stay in vaults and least privilege IAM roles are used.
- Client Security: review CSP headers, iframe restrictions, service-worker behavior, offline caches, and clipboard/file access.
- Monitoring & Incident Response: confirm critical actions emit audit logs/metrics, alerts cover new flows, and rate limits exist.
- Privacy & Compliance: validate data retention, consent tracking, and regional storage requirements when touching user data.

Highlight any blocking issues, unclear assumptions, or areas needing dedicated penetration testing.
