# Python method reference

All methods exist on Client and AsyncClient; await async calls.

| Method | HTTP |
| --- | --- |
| `customer_config_public(**fields)` | `POST /customer/config` |
| `workflow_latest(**fields)` | `POST /workflow/latest` |
| `transfer_instant(**fields)` | `POST /transfers/instant` |
| `transfer_instant_otp(**fields)` | `POST /transfers/instant/otp` |
| `transfer_iban_otp(**fields)` | `POST /transfers/iban/otp` |
| `transfer_order(**fields)` | `POST /transfers/order` |
| `validate_mobile(**fields)` | `POST /auth/mobile/validate` |
| `otp_request(**fields)` | `POST /auth/otp/request` |
| `otp(**fields)` | `POST /auth/otp` |
| `login(username: str \| None = None, password: str \| None = None, mobile_number: str \| None = None)` | `POST /auth/login` |
| `cards()` | `GET /cards` |
| `accounts()` | `GET /accounts` |
| `profile(**fields)` | `POST /profile` |
| `config(**fields)` | `GET /config` |
| `config_save(**fields)` | `POST /config` |
| `contacts(**fields)` | `GET /contacts` |
| `workflow_active(**fields)` | `GET /workflow/active` |
| `requests(**fields)` | `POST /requests` |
| `cartable(**fields)` | `POST /cartable` |
| `accounts_with_cards(**fields)` | `GET /accounts/with-cards` |
| `home(**fields)` | `GET /home` |
| `wallet_token(**fields)` | `POST /wallet/token` |
| `banners(**fields)` | `GET /banners` |
| `menus(**fields)` | `GET /menus` |
| `account_balance(account: str)` | `GET /accounts/{number}/balance` |
| `transfer_limits(**fields)` | `POST /transfers/limits` |
| `workflow_cancel(**fields)` | `POST /workflow/cancel` |
| `card_owner(**fields)` | `POST /transfers/card/owner` |
| `iban(card_number: str)` | `GET /cards/{number}/iban` |
| `transfer_methods(**fields)` | `POST /transfers/methods` |
| `workflow_create(**fields)` | `POST /workflow/create` |
| `workflow_state(**fields)` | `POST /workflow/state` |
| `workflow_event(**fields)` | `POST /workflow/event` |
| `card_password_status(**fields)` | `POST /cards/password/status` |
| `transfer_otp(**fields)` | `POST /transfers/card/otp` |
| `transfer_card(**fields)` | `POST /transfers/card` |
| `owner(iban: str)` | `GET /owner/iban/{iban}` |
| `payment_id_check(**fields)` | `POST /payments/id/check` |
| `parameters(**fields)` | `POST /parameters` |
| `sayah_inquiry(**fields)` | `POST /transfers/sayah` |
| `account_transfer_otp(**fields)` | `POST /transfers/account/otp` |
| `transfer_iban(**fields)` | `POST /transfers/iban` |
| `payment_orders(**fields)` | `POST /reports/payment-orders` |
| `transfer_ach(**fields)` | `POST /transfers/ach` |
| `transactions(account: str, page: int = 0, size: int = 10, **filters: Any)` | `GET /transactions` |
| `balance_average(**fields)` | `POST /balances/average` |
| `transaction(statement_id: str)` | `GET /transactions/{id}` |
| `transfer_report(**fields)` | `POST /reports/transfers` |
| `receipts(**fields)` | `POST /receipts` |
| `services(**fields)` | `GET /services` |
| `customer_cards(**fields)` | `GET /customer/cards` |
| `transfer_instant_fixed(**fields)` | `POST /transfers/fixed/instant` |
| `transfer_iban_fixed(**fields)` | `POST /transfers/fixed/iban` |
| `transfer_instant_sms_request(**fields)` | `POST /transfers/sms/instant/otp` |
| `transfer_instant_sms(**fields)` | `POST /transfers/sms/instant` |
| `transfer_iban_sms_request(**fields)` | `POST /transfers/sms/iban/otp` |
| `transfer_iban_sms(**fields)` | `POST /transfers/sms/iban` |
| `pol(account: str, iban: str, amount: int, password: str, *, reason: str, branch_code: str, **options: Any)` | `POST /pol` |
| `sheba(account: str, iban: str, amount: int, password: str, *, reason: str, **options: Any)` | `POST /sheba` |
| `pol_sms(account: str, iban: str, amount: int, code: str, *, reason: str, branch_code: str, **options: Any)` | `POST /pol/sms` |
| `sheba_sms(account: str, iban: str, amount: int, code: str, *, reason: str, **options: Any)` | `POST /sheba/sms` |
| `pol_code(account: str, iban: str, amount: int, *, username: str \| None = None, customer_number: str \| None = None)` | `POST /pol/code` |
| `sheba_code(account: str, iban: str, amount: int, *, username: str \| None = None, customer_number: str \| None = None)` | `POST /sheba/code` |
| `status()` | `GET /auth/session` |
| `check_session()` | `POST /auth/session/check` |
| `ensure_session(username: str \| None = None, password: str \| None = None, mobile_number: str \| None = None)` | `POST /auth/session/ensure` |
| `logout()` | `POST /auth/logout` |
| `deposits()` | `GET /deposits` |
| `cards_all(**fields)` | `GET /cards/all` |
| `deposits_all(**fields)` | `GET /deposits/all` |
| `balance()` | `GET /balance` |
| `balance_cards(**fields)` | `GET /balances/cards` |
| `balance_deposits(**fields)` | `GET /balances/deposits` |
| `transactions_latest(**fields)` | `GET /transactions/latest` |
| `transaction_find(**fields)` | `GET /transactions/find/{code}` |
| `health()` | `GET /health` |
