# parsian-api — Python SDK

Install name: `parsian-api`. Import name: `parsianapi`. Requires Python 3.10 or later.
This SDK connects to the project's local HTTP service. Start the Node.js service separately before using the SDK or Python CLI.

```powershell
python -m pip install parsian-api
```

The command above is available after the first PyPI release. To install from the repository before publication, run this from the repository root:

```powershell
python -m pip install ./python
```

## One-time configuration

Create a `.env` file in your application's working directory, or copy the example from the repository root:

```dotenv
PARSIAN_API_URL=http://127.0.0.1:3101/v1
PARSIAN_API_KEY="YOUR_SERVICE_KEY"
PARSIAN_USER="YOUR_USERNAME"
PARSIAN_PASS="YOUR_PASSWORD"
PARSIAN_MOBILE="YOUR_MOBILE"
```

```python
from parsianapi import Client

with Client() as bank:
    print(bank.login())
    print(bank.check_session())
    print(bank.accounts())
    print(bank.cards())
    print(bank.balance())
    print(bank.transactions("YOUR_ACCOUNT", page=0, size=10))
```

The SDK reads `.env` from the current working directory. Use `Client(env_file="path/to/.env")` to select another file, or `env_file=False` to disable file loading.
Explicit constructor arguments override environment variables; environment variables override file values.
Quote values containing spaces or `#`. Variable interpolation is disabled, so passwords are read literally.
Keep your populated `.env` private; publish only `.env.example`.

## Async client

```python
import asyncio
from parsianapi import AsyncClient

async def main():
    async with AsyncClient() as bank:
        print(await bank.check_session())
        print(await bank.balance())

asyncio.run(main())
```

## POL and IBAN transfers

Use `pol` for instant transfers and `sheba` for IBAN/PAYA transfers with a fixed transfer password:

```python
from parsianapi import Client

with Client() as bank:
    result = bank.pol(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        password="YOUR_FIXED_TRANSFER_PASSWORD",
        reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
    # IBAN transfer with a fixed password:
    # bank.sheba(account, iban, amount, password, reason=reason)
```

Request an SMS code separately, then submit the transfer:

```python
with Client() as bank:
    bank.pol_code("YOUR_ACCOUNT", "YOUR_IBAN", 10000)
    # After receiving the SMS code:
    result = bank.pol_sms(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        code="YOUR_SMS_CODE", reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
```

Use `sheba_code` and `sheba_sms` for IBAN transfers with SMS verification.
Card transfers use `card_otp` and `card_transfer`.
Amounts are integer Iranian rials (IRR). Keep account numbers, card numbers and passwords as strings to preserve leading zeros.
Choose the reason code and branch from the actual transaction details; the SDK does not infer them.
Card verification uses the OTP request's `tracking_number` and the transfer's `transaction_number`; these identifiers are not interchangeable.

## All API operations

Both sync and async clients cover all 76 local API operations.
Generated method names replace command hyphens with underscores. Convenience methods such as `pol`, `transactions`, `login` and `find_transaction` have dedicated signatures; consult the method reference for exact names and arguments.
Use `operation()` for command-based access. Field names can use snake_case:

```python
with Client() as bank:
    print(bank.operation("banners", banner_mode="YOUR_MODE"))
    print(bank.operation("workflow-state", workflow_instance_id="YOUR_INSTANCE"))
```

See the [method reference](https://github.com/DevURANIUM/parsian-api/blob/main/python/docs/reference.md).
Responses preserve nested fields returned by the service.

## Error handling

```python
from parsianapi import Client, ApiError, TransportError, ProtocolError

try:
    with Client() as bank:
        print(bank.balance())
except ApiError as error:
    print(error.status_code, error.code, error.next_action)
except (TransportError, ProtocolError) as error:
    print(error.request_may_have_succeeded)
```

Requests are never retried automatically, and redirects are not followed.
A connection or response error during a POST can leave the outcome uncertain. Check the bank's transaction report before resubmitting a transfer.

## Python CLI

```powershell
parsian-api login
parsian-api check-session
parsian-api accounts
parsian-api balance
parsian-api transactions YOUR_ACCOUNT 0 10
parsian-api pol YOUR_ACCOUNT YOUR_IBAN 10000
parsian-api pol-code YOUR_ACCOUNT YOUR_IBAN 10000
parsian-api pol-sms YOUR_ACCOUNT YOUR_IBAN 10000
parsian-api --help
```

You can also run the CLI with `python -m parsianapi`.
The Python CLI requires the HTTP service to be running. The Node CLI can call the bank directly.
Use `--field name=value` for advanced fields. Place `--json-errors` before the command name.
The `dry-run` option is available only in the Node CLI.
Login does not prompt when all required credentials are configured in `.env`. Interactive password input is hidden.

## Development

Run these commands from the `python` directory:

```powershell
python -m pip install -e . pytest build twine
python -m pytest -q
python -m build
python -m twine check dist/*
```

Financial tests use a simulated bank and do not send real transfers or SMS messages.
