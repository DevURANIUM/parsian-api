## انتقال پل و شبا با رمز پیامکی

ابتدا رمز پیامکی را درخواست کنید و سپس انتقال را با کد دریافتی ثبت کنید. پیامک به شماره ثبت‌شده بانک می‌رود. ورود اطلاعات کامندی است؛ نیازی به ساخت فایل یا بدنه سریال‌شده نیست.

### پل / Instant

#### دریافت رمز

```powershell
node cli.js pol-code YOUR_ACCOUNT YOUR_IBAN 10000 --username YOUR_USER --customer-number YOUR_CUSTOMER_NUMBER
```

```sh
curl -X POST 'http://127.0.0.1:3101/v1/pol/code' -H 'x-api-key: YOUR_API_KEY' --data-urlencode 'from=YOUR_ACCOUNT' --data-urlencode 'to=YOUR_IBAN' --data-urlencode 'amount=10000' --data-urlencode 'username=YOUR_USER' --data-urlencode 'customerNumber=YOUR_CUSTOMER_NUMBER'
```

در مرحله درخواست رمز، password نفرستید. username و customerNumber در اجرای واقعی می‌توانند از نشست ورود فعلی خوانده شوند.

#### ثبت انتقال

```powershell
node cli.js pol-sms YOUR_ACCOUNT YOUR_IBAN 10000
```

دلیل انتقال و کد شعبه موردنیاز در ترمینال پرسیده می‌شوند؛ می‌توانید PARSIAN_REASON و PARSIAN_BRANCH را یک بار تنظیم کنید. رمز نیز مخفی پرسیده می‌شود؛ کد پیامکی همان انتقال را وارد کنید. برای اجرای غیرتعاملی --password-file مسیر فایل متنی رمز را بدهید. --password VALUE هم پشتیبانی می‌شود، ولی مقدار آن در تاریخچه فرمان باقی می‌ماند.

```powershell
node cli.js pol-sms --source-account YOUR_ACCOUNT --iban YOUR_IBAN --amount 10000 --password YOUR_PASSWORD --dry-run
```

```sh
curl -X POST 'http://127.0.0.1:3101/v1/pol/sms' -H 'x-api-key: YOUR_API_KEY' --data-urlencode 'from=YOUR_ACCOUNT' --data-urlencode 'to=YOUR_IBAN' --data-urlencode 'amount=10000' --data-urlencode 'reason=LMAP' --data-urlencode 'branch=YOUR_BRANCH' --data-urlencode 'pass=YOUR_PASSWORD'
```

### شبا / پایا

#### دریافت رمز

```powershell
node cli.js sheba-code YOUR_ACCOUNT YOUR_IBAN 10000 --username YOUR_USER --customer-number YOUR_CUSTOMER_NUMBER
```

```sh
curl -X POST 'http://127.0.0.1:3101/v1/sheba/code' -H 'x-api-key: YOUR_API_KEY' --data-urlencode 'from=YOUR_ACCOUNT' --data-urlencode 'to=YOUR_IBAN' --data-urlencode 'amount=10000' --data-urlencode 'username=YOUR_USER' --data-urlencode 'customerNumber=YOUR_CUSTOMER_NUMBER'
```

در مرحله درخواست رمز، password نفرستید. username و customerNumber در اجرای واقعی می‌توانند از نشست ورود فعلی خوانده شوند.

#### ثبت انتقال

```powershell
node cli.js sheba-sms YOUR_ACCOUNT YOUR_IBAN 10000
```

دلیل انتقال و کد شعبه موردنیاز در ترمینال پرسیده می‌شوند؛ می‌توانید PARSIAN_REASON و PARSIAN_BRANCH را یک بار تنظیم کنید. رمز نیز مخفی پرسیده می‌شود؛ کد پیامکی همان انتقال را وارد کنید. برای اجرای غیرتعاملی --password-file مسیر فایل متنی رمز را بدهید. --password VALUE هم پشتیبانی می‌شود، ولی مقدار آن در تاریخچه فرمان باقی می‌ماند.

```powershell
node cli.js sheba-sms --source-account YOUR_ACCOUNT --iban YOUR_IBAN --amount 10000 --password YOUR_PASSWORD --dry-run
```

```sh
curl -X POST 'http://127.0.0.1:3101/v1/sheba/sms' -H 'x-api-key: YOUR_API_KEY' --data-urlencode 'from=YOUR_ACCOUNT' --data-urlencode 'to=YOUR_IBAN' --data-urlencode 'amount=10000' --data-urlencode 'reason=LMAP' --data-urlencode 'pass=YOUR_PASSWORD'
```

### گزینه‌ها و پاسخ

sourceAccount حساب مبدا، iban شبای مقصد، amount عدد صحیح ریالی و reason کد دلیل معتبر بانک است. LMAP فقط کد دیده‌شده در HAR است؛ دلیل مناسب عملیات خود را انتخاب کنید. branchCode در پل لازم است. گزینه‌های --first-name، --last-name، --owner-name، --transfer-description و --is-save-to-contact true|false نیز قابل استفاده‌اند. مقدارهای YOUR_* را جایگزین کنید. روش رمز در نام فرمان و آدرس مشخص است؛ passwordMode متناقض رد می‌شود.

API فرم application/x-www-form-urlencoded را می‌پذیرد؛ نمونه‌های cURL نوع فرم را خودکار تنظیم می‌کنند. فیلدها در بدنه POST هستند و رمز را در URL نگذارید. پاسخ API همان پاسخ استاندارد بانک است. --dry-run درخواست را ارسال نمی‌کند و رمزها را پنهان می‌کند؛ در پیش‌نمایش باید رمز نمایشی را صریح بدهید تا پرسش تعاملی انجام نشود. هیچ درخواست انتقالی خودکار تکرار نمی‌شود.
