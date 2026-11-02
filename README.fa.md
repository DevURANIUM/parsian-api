# parsian-api

**سرویس محلی HTTP، ابزار خط فرمان و کتابخانه پایتون پارسیان پلاس.**

[English](README.md) · [مستندات آنلاین](https://apibank.vcpu.tech/parsian/) · [راهنمای پایتون](python/README.md)

این پروژه ۷۶ عملیات محلی برای حساب، کارت، موجودی، گردش، رسید، انتقال کارت، پل و شبا ارائه می‌کند. رمز ثابت و پیامکی مسیرهای مستقل دارند. پروژه غیررسمی است و تأیید یا وابستگی به بانک را ادعا نمی‌کند.

## ساختار

کتابخانه و CLI پایتون به سرویس Node.js خودتان وصل می‌شوند. Node مسئول پروتکل بانک و نشست است؛ سایت مستندات، API بانکی شما نیست. هر سرویس یک نشست مشترک دارد؛ برای حساب مستقل، سرویس و پوشه داده مستقل بسازید.

نام نصب `parsian-api` و نام import برابر `parsianapi` است. نسخه سرویس 0.5.0 و نسخه اولیه کتابخانه 0.1.0 است. نسخه پایتون بعد از اجرای انتشار در PyPI قابل نصب عمومی خواهد بود؛ فعلاً نصب از سورس هم ممکن است.

## شروع سریع

Node.js 22+ و برای SDK، Python 3.10+ لازم است.

```powershell
git clone https://github.com/DevURANIUM/parsian-api.git
cd parsian-api
npm ci
Copy-Item .env.example .env
notepad .env
```

اطلاعات را فقط یک بار در `.env` وارد کنید:

```dotenv
PARSIAN_USER="YOUR_USERNAME"
PARSIAN_PASS="YOUR_PASSWORD"
PARSIAN_MOBILE="YOUR_MOBILE"
PARSIAN_API_KEY="YOUR_SERVICE_KEY"
```

اگر مقدار شامل فاصله یا # است، کوتیشن را نگه دارید. فایل خصوصی `.env` وارد Git نمی‌شود. Node فایل کنار `server.js` را خودکار می‌خواند و متغیر محیطی موجود بر فایل اولویت دارد.

```powershell
node cli.js login
node cli.js check-session
node cli.js accounts
node cli.js balance
node cli.js transactions YOUR_ACCOUNT 0 10
npm start
```

پیش‌فرض HTTP برابر `http://127.0.0.1:3101/v1` است. CLI مستقل و سرور نشست مشترک دارند؛ برای تغییر نشست از CLI مستقل، سرویس را متوقف کنید یا پوشه داده جدا بدهید. CLI پایتون از صف HTTP سرویس استفاده می‌کند.

## نصب و استفاده پایتون

بعد از انتشار اولیه:

```powershell
python -m pip install parsian-api
```

نصب از سورس فعلی:

```powershell
python -m pip install ./python
```

```python
from parsianapi import Client

with Client() as bank:
    print(bank.login())  # خواندن اطلاعات از .env
    print(bank.check_session())
    print(bank.accounts())
    print(bank.balance())
    print(bank.transactions("YOUR_ACCOUNT", page=0, size=10))
```

پایتون `.env` را از پوشه فعلی می‌خواند؛ با `Client(env_file="path/to/.env")` مسیر صریح بدهید. `env_file=False` خواندن فایل را غیرفعال می‌کند. آرگومان صریح سازنده، سپس متغیر محیطی و سپس فایل اولویت دارند. فایل رمزها را به‌صورت متن روی دیسک خودتان نگه می‌دارد؛ آن را منتشر نکنید.

### ناهمگام

```python
import asyncio
from parsianapi import AsyncClient

async def main():
    async with AsyncClient() as bank:
        print(await bank.check_session())
        print(await bank.balance())

asyncio.run(main())
```

### انتقال

```python
with Client() as bank:
    result = bank.pol(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        password="YOUR_FIXED_TRANSFER_PASSWORD",
        reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
```

```python
with Client() as bank:
    bank.pol_code("YOUR_ACCOUNT", "YOUR_IBAN", 10000)
    # پس از دریافت کد تازه:
    result = bank.pol_sms(
        "YOUR_ACCOUNT", "YOUR_IBAN", 10000,
        code="YOUR_SMS_CODE", reason="YOUR_REASON_CODE", branch_code="YOUR_BRANCH",
    )
```

شبا: `sheba`، `sheba_code` و `sheba_sms`. کارت: `card_otp` و `card_transfer`. مبلغ عدد صحیح ریالی است؛ شماره‌ها و رمزها رشته‌اند. دلیل انتقال و شعبه را براساس همان عملیات انتخاب کنید؛ کتابخانه حدس نمی‌زند. مثال‌ها با داده واقعی عملیات واقعی ثبت می‌کنند. هیچ retry خودکاری وجود ندارد؛ پس از timeout ابتدا گزارش بانک را بررسی کنید.

## فرمان‌های کوتاه

```powershell
node cli.js pol YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js pol-code YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js pol-sms YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba-code YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba-sms YOUR_ACCOUNT YOUR_IBAN 10000
```

رمزها مخفی پرسیده می‌شوند. Node CLI گزینه `--dry-run` برای پیش‌نمایش بدون ارسال دارد. نام‌های بلند قبلی برای سازگاری حفظ شده‌اند.

CLI پایتون به سرویس روشن نیاز دارد:

```powershell
parsian-api login
parsian-api check-session
parsian-api accounts
parsian-api balance
parsian-api transactions YOUR_ACCOUNT 0 10
parsian-api pol YOUR_ACCOUNT YOUR_IBAN 10000
parsian-api --help
```

`python -m parsianapi` معادل است. برای فیلد پیشرفته از `--field NAME=VALUE` استفاده کنید. گزینه dry-run در CLI پایتون پیاده نشده است. `--json-errors` پیش از فرمان، خطای ساختاریافته روی stderr می‌دهد؛ کد خروج خطا ۱ است.

## HTTP، نشست و تنظیمات

هدر `x-api-key` کلید سرویس است و با رمز بانک تفاوت دارد. `health` عمومی است. بدنه POST فرم معمولی است و فایل ورودی لازم نیست.

```powershell
curl.exe http://127.0.0.1:3101/v1/health
curl.exe http://127.0.0.1:3101/v1/accounts -H "x-api-key: YOUR_SERVICE_KEY"
```

`status` وضعیت محلی است؛ `check-session` اعتبار را نزد بانک بررسی می‌کند. `ensure-session` با اطلاعات کامل می‌تواند یک بار login کند. تأیید موبایل پارسیان با جریان دستگاه سامان یکسان نیست و به‌صورت حدسی خودکار اجرا نمی‌شود.

`ApiError` شامل `status_code`، `code`، `bank_status`، `next_action` و `payload` است. `TransportError` و `ProtocolError` با `request_may_have_succeeded` نتیجه نامشخص درخواست نوشتنی را مشخص می‌کنند. پاسخ‌ها بدون حذف فیلدهای تو‌در‌تو حفظ می‌شوند؛ SDK redirect را دنبال نمی‌کند.

| متغیر | کاربرد |
| --- | --- |
| PARSIAN_USER / PARSIAN_PASS / PARSIAN_MOBILE | اطلاعات ورود بانک |
| PARSIAN_API_KEY | کلید مشترک سرویس و SDK |
| PARSIAN_API_URL | آدرس سرویس برای پایتون |
| PARSIAN_HOST / PARSIAN_PORT | پیش‌فرض 127.0.0.1 و 3101 |
| PARSIAN_DATA_DIR | محل نشست محلی |
| PARSIAN_ACCOUNT / PARSIAN_REASON / PARSIAN_BRANCH | پیش‌فرض‌های اختیاری CLI |

خارج localhost کلید لازم است؛ اتصال راه دور را با HTTPS محافظت کنید.

## توسعه و انتشار

```powershell
npm ci
npm test
python -m pip install -e ./python pytest build twine
python -m pytest python/tests -q
python -m build python
python -m twine check python/dist/*
```

تست‌های مالی شبیه‌سازی‌شده‌اند و پول یا پیامک واقعی ارسال نمی‌کنند. بسته wheel فقط SDK پایتون است؛ سورس GitHub هر دو بخش Node و Python را دارد.

[راهنمای انتشار](docs/PUBLISH.fa.md) · [مرجع API](local-openapi.json) · [مشارکت](CONTRIBUTING.md) · [MIT](LICENSE)
