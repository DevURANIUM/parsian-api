# Security

Do not publish credentials, service keys, session IDs, HAR files, or unredacted bank data.
Report a reproducible, redacted security issue through the repository's private security
reporting feature when enabled. Do not open public issues containing secret values.

Use HTTPS outside a local machine and a distinct service key per deployment. Each Node
service owns one shared bank session; use isolated services/data directories per account.
The SDK never follows redirects or automatically retries payment submissions.
