# parsian-api

<img src="assets/parsian.svg" alt="Parsian Plus" width="64">

**Parsian Plus integration with a local HTTP service, a standalone Node.js CLI, and a Python SDK.**

[English](README.md) · [فارسی](README.fa.md) · [Documentation](https://apibank.vcpu.tech/parsian/) · [Python guide](python/README.md)

[![CI](https://github.com/DevURANIUM/parsian-api/actions/workflows/ci.yml/badge.svg)](https://github.com/DevURANIUM/parsian-api/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/parsian-api)](https://pypi.org/project/parsian-api/)
[![Python](https://img.shields.io/pypi/pyversions/parsian-api)](https://pypi.org/project/parsian-api/)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Read deposits, cards, balances, statements and receipts, or integrate card, POL/instant and IBAN/PAYA transfers through **76 documented local operations**. Fixed-password and SMS-code transfers have separate commands and API routes.

This community project is independent of Parsian Bank. Operation availability, authentication and settlement are controlled by the bank.

## Choose an interface

| Interface | Role | HTTP server needed? |
| --- | --- | --- |
| `npm start` | Run the local bank adapter | Starts it |
| `node cli.js` | Work directly with the local bank session | No |
| `from parsianapi import Client, AsyncClient` | Integrate from Python | Yes |
| `parsian-api` / `python -m parsianapi` | Python command-line client | Yes |

The Python package talks to your own Node.js service. It does not call the bank independently. The public documentation site is not your banking API URL.

**Package names:** install `parsian-api`; import `parsianapi`. Node service **0.5.0** and Python SDK **0.1.0** have independent version numbers. The PyPI installation command becomes available after the first successful package publication; source installation works immediately.

## Get started

Requires Node.js 22+. Python SDK requires Python 3.10+.

```powershell
git clone https://github.com/DevURANIUM/parsian-api.git
cd parsian-api
npm ci
Copy-Item .env.example .env
notepad .env
```

Fill your own settings once:

```dotenv
PARSIAN_API_KEY="YOUR_SERVICE_KEY"
PARSIAN_USER="YOUR_BANK_USERNAME"
PARSIAN_PASS="YOUR_BANK_PASSWORD"
PARSIAN_MOBILE="YOUR_REGISTERED_MOBILE"
```

Keep `.env` private. Use quotes around values containing spaces or `#`. The Node commands load the project-root `.env` automatically; existing shell variables take priority.

```powershell
node cli.js login
node cli.js check-session
node cli.js accounts
node cli.js balance
node cli.js transactions YOUR_ACCOUNT 0 10
```

Start the API service when using HTTP or Python:

```powershell
npm start
```

The default URL is `http://127.0.0.1:3101/v1`. The server and standalone CLI share one session directory. Avoid concurrent session-changing standalone commands while that server is using it; use the Python CLI or HTTP interface for queued access instead.

## Python

After publishing to PyPI:

```powershell
python -m pip install parsian-api
```

Before the first publication, install from the cloned repository:

```powershell
python -m pip install ./python
```

Run from the folder containing `.env`, or pass `env_file` explicitly:

```python
from parsianapi import Client

with Client() as bank:
    print(bank.login())  # Reads USER, PASS and MOBILE from .env
    print(bank.check_session())
    print(bank.accounts())
    print(bank.cards())
    print(bank.balance())
    print(bank.transactions("YOUR_ACCOUNT", page=0, size=10))
```

For a different service:

```python
with Client(
    base_url="http://127.0.0.1:3101/v1",
    api_key="YOUR_SERVICE_KEY",
    env_file=False,
) as bank:
    print(bank.latest_transactions("YOUR_ACCOUNT", limit=10))
```

Closing the client closes its HTTP connections; it does not log out the bank account.

### Async

```python
import asyncio
from parsianapi import AsyncClient

async def main():
    async with AsyncClient() as bank:
        print(await bank.check_session())
        print(await bank.balance())

asyncio.run(main())
```

### Transfers

Explicit fixed-password methods:

```python
with Client() as bank:
    result = bank.pol(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        password="YOUR_FIXED_TRANSFER_PASSWORD",
        reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
    # IBAN/PAYA:
    # result = bank.sheba(account, iban, amount, password, reason=reason)
```

SMS stages are independent:

```python
with Client() as bank:
    bank.pol_code("YOUR_ACCOUNT", "YOUR_IBAN", 10000)
    # Collect the newly received code in your application.
    result = bank.pol_sms(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000, code="YOUR_SMS_CODE",
        reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
```

Use `sheba_code()` / `sheba_sms()` for IBAN/PAYA, and `card_otp()` / `card_transfer()` for cards. Pass the correct payment-purpose code and source-branch information; the SDK does not choose these business details for you. Money is in IRR, supplied as a positive integer. Keep identifiers and passwords as strings.

These examples submit real instructions when you replace the placeholders and execute them. Payment requests and SMS sends are never retried automatically. An uncertain timeout must be reconciled through bank reports before another submission.

### Errors and complete responses

```python
from parsianapi import Client, ApiError, TransportError, ProtocolError

try:
    with Client() as bank:
        print(bank.balance())
except ApiError as error:
    print(error.status_code, error.code, error.next_action)
    # error.payload preserves the complete service response.
except (TransportError, ProtocolError) as error:
    print(error.request_may_have_succeeded)
```

Successful responses are returned without replacing missing data or truncating nested fields. The SDK rejects redirects and does not print service keys or bank credentials in its representation or exception message.

## Short commands

```powershell
node cli.js pol YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js pol-code YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js pol-sms YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba-code YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba-sms YOUR_ACCOUNT YOUR_IBAN 10000
```

`pol` and `sheba` use a fixed transfer password. The `-code` commands request SMS; the `-sms` commands submit with that code. Missing details are requested interactively and passwords are hidden. Set `PARSIAN_ACCOUNT`, `PARSIAN_REASON` and `PARSIAN_BRANCH` for optional defaults. Node `--dry-run` creates a redacted preview without sending anything.

The Python CLI uses the running service:

```powershell
parsian-api login
parsian-api check-session
parsian-api accounts
parsian-api balance
parsian-api transactions YOUR_ACCOUNT 0 10
parsian-api pol YOUR_ACCOUNT YOUR_IBAN 10000
parsian-api --help
```

For the advanced Python CLI, use `--field NAME=VALUE`; the Python API accepts snake_case keyword fields. The Python CLI does not implement Node's `--dry-run` option. Successful output goes to stdout; errors go to stderr with exit code 1. Put `--json-errors` before the command for structured errors.

## HTTP API

Send `x-api-key` when a service key is configured. `health` is public. Request fields use ordinary HTTP forms; no input file is required.

```powershell
curl.exe "http://127.0.0.1:3101/v1/health"
curl.exe "http://127.0.0.1:3101/v1/accounts" -H "x-api-key: YOUR_SERVICE_KEY"
curl.exe -X POST "http://127.0.0.1:3101/v1/pol" -H "x-api-key: YOUR_SERVICE_KEY" --data-urlencode "from=YOUR_ACCOUNT" --data-urlencode "to=YOUR_IBAN" --data-urlencode "amount=10000" --data-urlencode "reason=YOUR_REASON_CODE" --data-urlencode "branch=YOUR_BRANCH" --data-urlencode "pass=YOUR_TRANSFER_PASSWORD"
```

| Method | Path after `/v1` | Purpose |
| --- | --- | --- |
| GET | `/accounts`, `/cards`, `/balance` | Account data |
| GET | `/transactions?account=...&page=0&size=10` | Statements |
| GET | `/transactions/{id}` | Receipt by statement ID |
| POST | `/auth/login` | Bank login |
| POST | `/auth/session/check` | Validate bank session |
| POST | `/auth/session/ensure` | Validate and optionally sign in once |
| POST | `/pol`, `/sheba` | Fixed-password transfer |
| POST | `/pol/code`, `/sheba/code` | Request transfer SMS |
| POST | `/pol/sms`, `/sheba/sms` | Submit with SMS code |
| POST | `/transfers/card` | Card transfer |

Forms accept nested names such as `parent.child`; object arrays use `0.field`. Existing long commands and routes are retained for compatibility. The [OpenAPI contract](local-openapi.json) and [Postman collection](local-postman_collection.json) describe all 76 local operations. The unprefixed local routes remain available too.

## Environment settings

| Setting | Purpose / default |
| --- | --- |
| `PARSIAN_USER`, `PARSIAN_PASS`, `PARSIAN_MOBILE` | Bank login credentials |
| `PARSIAN_API_KEY` | Service key, shared by server and SDK |
| `PARSIAN_API_URL` | Python service URL; defaults to `http://127.0.0.1:3101/v1` |
| `PARSIAN_HOST`, `PARSIAN_PORT` | Server bind; defaults to `127.0.0.1`, `3101` |
| `PARSIAN_DATA_DIR` | Session directory, default `data/` |
| `PARSIAN_ACCOUNT` | Default account for supported standalone CLI commands |
| `PARSIAN_REASON`, `PARSIAN_BRANCH` | Optional Node/Python CLI transfer defaults |

The Python SDK reads `.env` from the current directory, or an explicit `env_file`. Explicit constructor arguments override shell variables, which override file values. Node reads the `.env` next to `server.js` regardless of the working directory. Credentials in this file are plaintext on your own disk; never upload it. The checked-in template contains no real credentials.

One server manages one shared bank session. Use separate instances and data directories for separate bank accounts. Outside localhost a service key is required; protect remote connections with HTTPS.

## Authentication notes

A stored session is not evidence that the bank still accepts it. `status()` reports local state; `check_session()` makes a bank request. For an expired session, sign in again, or use `ensure_session()` with complete environment credentials. Wrong credentials and expired sessions have distinct error codes.

Parsian's mobile-number verification is separate from Saman's device-verification flow. `request_otp()` and `verify_otp()` expose the observed mobile verification endpoints; they are not automatically triggered after every login. Password-change requirements must be handled in the bank app.

## Repository map

```text
server.js / client.js / domain-client.js  Bank adapter and HTTP routing
cli.js / transfer*.js / shortcuts.js      Standalone CLI and transfers
data/endpoints.json                      Sanitized bank schemas only
local-openapi.json                        Local service contract
python/                                  PyPI package, tests and examples
.github/workflows/ci.yml                  Test matrix
.github/workflows/workflow.yml            Tagged PyPI publishing
```

No captured bank traffic, personal accounts, sessions or populated `.env` is distributed. Public schemas describe observations; they are not an official bank specification. Financial behavior is tested with a simulated bank, not with new live payments.

## Develop and publish

```powershell
npm ci
npm test
python -m pip install -e ./python pytest build twine
python -m pytest python/tests -q
python python/tools/generate.py
python -m build python
python -m twine check python/dist/*
```

The initial distribution is `parsian-api==0.1.0`. Follow [publication instructions](docs/PUBLISH.fa.md) for the GitHub upload and exact PyPI Trusted Publisher fields. The publishing workflow expects a `python-v0.1.0` tag and the GitHub environment `pypi`.

See [CONTRIBUTING](CONTRIBUTING.md), [security notes](SECURITY.md), [changelog](CHANGELOG.md) and [MIT license](LICENSE).
