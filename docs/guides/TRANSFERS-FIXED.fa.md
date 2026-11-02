## انتقال پل و شبا با رمز ثابت

رمز ثابت انتقال حساب استفاده می‌شود و پیامک درخواست نمی‌شود. ورود اطلاعات کامندی است؛ نیازی به ساخت فایل یا بدنه سریال‌شده نیست.

### پل / Instant

#### ثبت انتقال

```powershell
node cli.js pol YOUR_ACCOUNT YOUR_IBAN 10000
```

دلیل انتقال و کد شعبه موردنیاز در ترمینال پرسیده می‌شوند؛ می‌توانید PARSIAN_REASON و PARSIAN_BRANCH را یک بار تنظیم کنید. رمز نیز مخفی پرسیده می‌شود؛ رمز ثابت انتقال حساب را وارد کنید. برای اجرای غیرتعاملی --password-file مسیر فایل متنی رمز را بدهید. --password VALUE هم پشتیبانی می‌شود، ولی مقدار آن در تاریخچه فرمان باقی می‌ماند.

```powershell
node cli.js pol --source-account YOUR_ACCOUNT --iban YOUR_IBAN --amount 10000 --password YOUR_PASSWORD --dry-run
```

```sh
curl -X POST 'http://127.0.0.1:3101/v1/pol' -H 'x-api-key: YOUR_API_KEY' --data-urlencode 'from=YOUR_ACCOUNT' --data-urlencode 'to=YOUR_IBAN' --data-urlencode 'amount=10000' --data-urlencode 'reason=LMAP' --data-urlencode 'branch=YOUR_BRANCH' --data-urlencode 'pass=YOUR_PASSWORD'
```

### شبا / پایا

#### ثبت انتقال

```powershell
node cli.js sheba YOUR_ACCOUNT YOUR_IBAN 10000
```

دلیل انتقال و کد شعبه موردنیاز در ترمینال پرسیده می‌شوند؛ می‌توانید PARSIAN_REASON و PARSIAN_BRANCH را یک بار تنظیم کنید. رمز نیز مخفی پرسیده می‌شود؛ رمز ثابت انتقال حساب را وارد کنید. برای اجرای غیرتعاملی --password-file مسیر فایل متنی رمز را بدهید. --password VALUE هم پشتیبانی می‌شود، ولی مقدار آن در تاریخچه فرمان باقی می‌ماند.

```powershell
node cli.js sheba --source-account YOUR_ACCOUNT --iban YOUR_IBAN --amount 10000 --password YOUR_PASSWORD --dry-run
```

```sh
curl -X POST 'http://127.0.0.1:3101/v1/sheba' -H 'x-api-key: YOUR_API_KEY' --data-urlencode 'from=YOUR_ACCOUNT' --data-urlencode 'to=YOUR_IBAN' --data-urlencode 'amount=10000' --data-urlencode 'reason=LMAP' --data-urlencode 'pass=YOUR_PASSWORD'
```

### گزینه‌ها و پاسخ

sourceAccount حساب مبدا، iban شبای مقصد، amount عدد صحیح ریالی و reason کد دلیل معتبر بانک است. LMAP فقط کد دیده‌شده در HAR است؛ دلیل مناسب عملیات خود را انتخاب کنید. branchCode در پل لازم است. گزینه‌های --first-name، --last-name، --owner-name، --transfer-description و --is-save-to-contact true|false نیز قابل استفاده‌اند. مقدارهای YOUR_* را جایگزین کنید. روش رمز در نام فرمان و آدرس مشخص است؛ passwordMode متناقض رد می‌شود.

API فرم application/x-www-form-urlencoded را می‌پذیرد؛ نمونه‌های cURL نوع فرم را خودکار تنظیم می‌کنند. فیلدها در بدنه POST هستند و رمز را در URL نگذارید. پاسخ API همان پاسخ استاندارد بانک است. --dry-run درخواست را ارسال نمی‌کند و رمزها را پنهان می‌کند؛ در پیش‌نمایش باید رمز نمایشی را صریح بدهید تا پرسش تعاملی انجام نشود. هیچ درخواست انتقالی خودکار تکرار نمی‌شود.
