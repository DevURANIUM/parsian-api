# parsian-api — کتابخانه پایتون

نام نصب: `parsian-api`؛ نام import: `parsianapi`. Python 3.10 یا جدیدتر لازم است.
این کتابخانه به سرویس HTTP پروژه متصل می‌شود؛ سرویس Node.js باید جداگانه روشن باشد.

```powershell
python -m pip install parsian-api
```

این دستور بعد از انتشار اولیه در PyPI قابل استفاده است. تا آن زمان از ریشه مخزن:

```powershell
python -m pip install ./python
```

## پیکربندی یک‌باره

فایل `.env` را کنار برنامه خود بسازید یا فایل نمونه ریشه مخزن را کپی کنید:

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

`.env` از پوشه فعلی خوانده می‌شود؛ برای آدرس مشخص از `Client(env_file="path/to/.env")` استفاده کنید.
آرگومان صریح سازنده بر متغیر محیطی و متغیر محیطی بر فایل اولویت دارد. `env_file=False` خواندن فایل را غیرفعال می‌کند.
مقادیر شامل فاصله یا # را داخل کوتیشن بگذارید. متغیرها در مقادیر فایل گسترش داده نمی‌شوند؛ رمز عیناً خوانده می‌شود.

## ناهمگام

```python
import asyncio
from parsianapi import AsyncClient

async def main():
    async with AsyncClient() as bank:
        print(await bank.check_session())
        print(await bank.balance())

asyncio.run(main())
```

## پل و شبا

```python
with Client() as bank:
    result = bank.pol(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        password="YOUR_FIXED_TRANSFER_PASSWORD",
        reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
    # شبا با رمز ثابت:
    # bank.sheba(account, iban, amount, password, reason=reason)
```

```python
with Client() as bank:
    bank.pol_code("YOUR_ACCOUNT", "YOUR_IBAN", 10000)
    # پس از دریافت پیامک:
    result = bank.pol_sms(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        code="YOUR_SMS_CODE", reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
```

برای شبا از `sheba_code` و `sheba_sms` استفاده کنید. برای کارت `card_otp` و `card_transfer` وجود دارد.
مبلغ عدد صحیح ریالی است؛ شماره‌ها و رمزها را رشته نگه دارید تا صفر اول حذف نشود.
دلیل انتقال و شعبه باید از اطلاعات واقعی عملیات انتخاب شوند؛ کتابخانه آن‌ها را حدس نمی‌زند.
کد کارت به tracking_number درخواست OTP و transaction_number انتقال وابسته است؛ این دو شناسه جایگزین هم نیستند.

## همه مسیرها

متدهای همگام و ناهمگام همه ۷۶ مسیر محلی را پوشش می‌دهند. نام فرمان با تبدیل خط تیره به underscore نام متد می‌شود.
متدهای ساده مثل `pol`، `transactions`، `login` و `find_transaction` امضای اختصاصی دارند.
برای دسترسی عمومی از operation استفاده کنید؛ کلیدها می‌توانند snake_case باشند:

```python
with Client() as bank:
    print(bank.operation("banners", banner_mode="YOUR_MODE"))
    print(bank.operation("workflow-state", workflow_instance_id="YOUR_INSTANCE"))
```

[مرجع متدها](docs/reference.md). پاسخ‌ها بدون حذف فیلدهای تو‌در‌تو حفظ می‌شوند.

## خطا

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

هیچ retry خودکاری وجود ندارد؛ redirect دنبال نمی‌شود. خطای اتصال هنگام POST می‌تواند نتیجه نامشخص داشته باشد؛ پیش از ارسال دوباره انتقال، گزارش بانک را بررسی کنید.

## CLI پایتون

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

`python -m parsianapi` معادل است. این CLI به سرویس روشن نیاز دارد؛ Node CLI مستقل است.
برای فیلدهای پیشرفته از `--field name=value` استفاده کنید. `--json-errors` باید پیش از نام فرمان باشد.
گزینه dry-run مخصوص Node CLI است و در Python CLI پیاده نشده است.
ورود با `.env` کامل چیزی نمی‌پرسد؛ در حالت تعاملی رمز مخفی پرسیده می‌شود.

## توسعه

```powershell
python -m pip install -e . pytest build twine
python -m pytest -q
python -m build
python -m twine check dist/*
```

آزمون‌های مالی از بانک شبیه‌سازی‌شده استفاده می‌کنند و پول یا پیامک واقعی ارسال نمی‌کنند.
