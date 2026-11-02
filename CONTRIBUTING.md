# Contributing

Use synthetic inputs in tests. Never commit .env, session files, credentials, receipts,
or browser captures. Keep the bank protocol and local route map consistent.

Run npm ci and npm test for Node changes. Install the Python package in editable mode
and run python -m pytest python/tests for SDK changes. Regenerate SDK route methods with
python python/tools/generate.py after changing the local OpenAPI contract.

Please report bugs with command names, versions and redacted error codes; omit account
identifiers, passwords, OTPs and service keys.
