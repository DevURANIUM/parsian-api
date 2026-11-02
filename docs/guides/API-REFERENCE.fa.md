# مرجع کامل پارسیان

# پارسیان پلاس

همان ساختار HTTP و CLI سامان؛ قرارداد ارتباط با بانک از HAR پارسیان گرفته شده است. آدرس API محلی با /v1 و هدر x-api-key است. این سایت فقط مستندات است. تمام ۴۷ درخواست بانکی در رابط محلی نگاشت دارند. داده‌های نمونه ساختگی‌اند و اجرای زنده بانک انجام نشده است.

## اجرا

Node.js 22 یا جدیدتر لازم است.

```powershell
npm ci
Copy-Item .env.example .env
notepad .env
npm start
node cli.js login
node cli.js accounts
node cli.js transactions YOUR_ACCOUNT 0 10
```

```sh
curl http://127.0.0.1:3101/v1/accounts -H "x-api-key: YOUR_API_KEY"
```

PARSIAN_HOST پیش‌فرض 127.0.0.1 و PARSIAN_PORT پیش‌فرض 3101 است. PARSIAN_DATA_DIR محل نشست را مشخص می‌کند. مسیرها هم با /v1 و هم بدون آن در دسترس‌اند. health معاف از کلید است. وقتی کلید تنظیم نشده، دسترسی فقط باید روی localhost باشد.

## ورود و نشست

```powershell
$env:PARSIAN_USER = "YOUR_USERNAME"
$env:PARSIAN_PASS = "YOUR_PASSWORD"
$env:PARSIAN_MOBILE = "YOUR_MOBILE"
node cli.js login
node cli.js status
node cli.js check-session
node cli.js ensure-session
node cli.js logout
```

فایل .env کنار server.js به‌صورت خودکار خوانده می‌شود. PARSIAN_USER، PARSIAN_PASS و PARSIAN_MOBILE را یک بار در آن وارد کنید تا ورود دوباره سؤال نپرسد. متغیر محیطی موجود بر فایل اولویت دارد؛ فایل خصوصی منتشر نمی‌شود.

Login پارسیان username، password، mobileNumber و additionalData دارد. کلاینت additionalData را با versionNumber="1.0" و platformType="Pwa" می‌فرستد مگر صریح تعیین شود. بررسی فایل JavaScript داخل HAR ارسال همین فیلدها را نشان داد؛ رمزگذاری سامان روی این درخواست اعمال نمی‌شود. Login موفق نشست data.sessionId را ذخیره می‌کند. نیاز به تغییر رمز در پاسخ گزارش می‌شود.

OTP: otp-request [mobileNo] درخواست پیامک و otp [code] [mobileNo] تأیید شماره است. این OTP همان جریان تأیید دستگاه سامان نیست و صرف تأیید موبایل ورود را تکمیل نمی‌کند. در HAR مقدار signedPassword رشته‌ای پنج‌رقمی است؛ کلاینت code را با همین نام بدون تبدیل رمزنگاری ارسال می‌کند. Login پیامک یا مرحله اضافه را خودکار اجرا نمی‌کند.

status وضعیت محلی unverified یا logged_out است؛ check-session با خواندن سپرده بانک را بررسی می‌کند. ensure-session ابتدا بررسی می‌کند و فقط در رد احراز هویت با ورودی کامل یک بار login می‌کند؛ عملیات مالی بازپخش نمی‌شود. logout محلی است.

## روش ارسال درخواست

در CLI فیلدها با --field VALUE و فیلد تو‌در‌تو با --parent.child VALUE وارد می‌شوند. در API از فرم application/x-www-form-urlencoded و نمونه cURL هر مسیر استفاده کنید. شناسه‌ها و رمزها رشته باقی می‌مانند؛ مبلغ و گزینه‌های عددی تبدیل می‌شوند. پاسخ API ساختار استاندارد بانک را حفظ می‌کند.

آرایه اسکالر با تکرار گزینه و آرایه شیء با شماره ردیف مانند --0.key VALUE ارسال می‌شود. برای مقدار nullable از null استفاده کنید. برای انتقال، مبلغ ریالی صحیح مثبت، حساب و شبای معتبر و روش رمز مناسب لازم است. هیچ درخواست مالی خودکار تکرار نمی‌شود.

## خطاها

کلید اشتباه 401، مسیر ناموجود 404، JSON نامعتبر 400، حجم بیش از حد 413، status غیرصفر بانک 422 و قطع اتصال، timeout یا پاسخ نامعتبر بانک 502 است. پاسخ خطا شامل error و در صورت وجود code، nextAction و bankStatus است. خطای LOGIN_FAILED مخصوص رد احراز هویت در مسیر عمومی ورود است؛ SESSION_EXPIRED نشست بانکی ردشده را مشخص می‌کند. status=0 بانک شرط موفقیت تجاری است؛ HTTP 200 به‌تنهایی کافی نیست. هیچ انتقالی retry خودکار ندارد. پس از timeout پیش از تکرار، گزارش و رسید را بررسی کنید. وضعیت محلی به معنی معتبر بودن نشست نیست.

PaymentIDCheckByCB در ضبط فقط نمونه HTTP 400 دارد. موفقیت آن تأیید نشده است. ساختار نمونه پاسخ موفق در این سایت از schema تولید می‌شود و پاسخ واقعی تازه بانک نیست.

## راهنمای کامل فرمان‌ها

داده‌ها را مستقیم با --field VALUE وارد کنید. شناسه‌ها، حساب، کارت و رمز رشته می‌مانند؛ مبلغ و گزینه‌های عددی تبدیل می‌شوند. فیلد تو‌در‌تو با نقطه و آرایه با تکرار گزینه نوشته می‌شود. در آرایه شیء، شماره ردیف را بنویسید: --0.key VALUE. برای مقدار nullable از واژه null استفاده کنید. هیچ فایل ورودی لازم نیست.

```powershell
node cli.js login
node cli.js accounts
node cli.js balance YOUR_ACCOUNT
node cli.js transactions YOUR_ACCOUNT 0 10
node cli.js transactions 0 10
node cli.js transaction YOUR_STATEMENT_ID
node cli.js transaction-find YOUR_CODE YOUR_ACCOUNT
node cli.js check-session
node cli.js ensure-session
node cli.js logout
node cli.js help
```

PARSIAN_USER، PARSIAN_PASS و PARSIAN_MOBILE برای ورود، PARSIAN_ACCOUNT برای حساب پیش‌فرض و PARSIAN_DATA_DIR برای محل نشست‌اند. نشست منقضی با login تازه جایگزین می‌شود؛ check-session فقط بررسی می‌کند. گردش بدون تاریخ صریح، ۳۰ روز اخیر را می‌خواند. --dry-run اجرای واقعی را متوقف می‌کند؛ در فرمان‌های مدیریتی و تجمیعی عمومی نیست. رمز در فرمان‌های انتقال اگر حذف شود مخفی پرسیده می‌شود.

## انتقال‌های کوتاه

```powershell
node cli.js pol YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js pol-code YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js pol-sms YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba-code YOUR_ACCOUNT YOUR_IBAN 10000
node cli.js sheba-sms YOUR_ACCOUNT YOUR_IBAN 10000
```

اطلاعات تکمیلی پرسیده می‌شوند و رمز مخفی وارد می‌شود. اگر PARSIAN_REASON و PARSIAN_BRANCH را تنظیم کنید، آن دو مقدار دوباره پرسیده نمی‌شوند.

<details><summary>فرمان‌های پیشرفته و قرارداد خام بانک</summary>

### general-validate-whitelisted-user

نام‌های کوتاه: `validate-mobile`

```powershell
node cli.js general-validate-whitelisted-user --mobile-number YOUR_VALUE --version-number 1 --dry-run
node cli.js general-validate-whitelisted-user --help
```

### otp-otp-generator-with-mobile-no

نام‌های کوتاه: `otp-request`

```powershell
node cli.js otp-otp-generator-with-mobile-no --mobile-no YOUR_VALUE --dry-run
node cli.js otp-otp-generator-with-mobile-no --help
```

### otp-validate-mobile-no-with-otp

نام‌های کوتاه: `otp-verify`، `otp`

```powershell
node cli.js otp-validate-mobile-no-with-otp --mobile-no YOUR_VALUE --signed-password YOUR_VALUE --dry-run
node cli.js otp-validate-mobile-no-with-otp --help
```

### user-login

نام‌های کوتاه: `login`

```powershell
node cli.js user-login --additional-data.first-time-login false --additional-data.platform-type YOUR_VALUE --additional-data.version-number YOUR_VALUE --mobile-number YOUR_VALUE --password YOUR_VALUE --username YOUR_VALUE --dry-run
node cli.js user-login --help
```

### inquiry-get-cards-with-amount

نام‌های کوتاه: `cards`

```powershell
node cli.js inquiry-get-cards-with-amount --dry-run
node cli.js inquiry-get-cards-with-amount --help
```

### inquiry-get-deposits

نام‌های کوتاه: `deposits`، `accounts`

```powershell
node cli.js inquiry-get-deposits --dry-run
node cli.js inquiry-get-deposits --help
```

### general-get-customer-config-detail-by-cif

نام‌های کوتاه: `config`

```powershell
node cli.js general-get-customer-config-detail-by-cif --dry-run
node cli.js general-get-customer-config-detail-by-cif --help
```

### inquiry-get-user-contact-with-contact-details

نام‌های کوتاه: `contacts`

```powershell
node cli.js inquiry-get-user-contact-with-contact-details --dry-run
node cli.js inquiry-get-user-contact-with-contact-details --help
```

### inquiry-get-customer-extra-data

نام‌های کوتاه: `profile`

```powershell
node cli.js inquiry-get-customer-extra-data --cif YOUR_VALUE --dry-run
node cli.js inquiry-get-customer-extra-data --help
```

### workflow-get-active-instances

نام‌های کوتاه: `workflow-active`

```powershell
node cli.js workflow-get-active-instances --dry-run
node cli.js workflow-get-active-instances --help
```

### my-request-get-my-requests

نام‌های کوتاه: `requests`

```powershell
node cli.js my-request-get-my-requests --request-type null --request-code null --status null --from-request-date null --to-request-date null --from-expire-date null --to-expire-date null --priority null --operational false --load-approval false --client-id null --description null --start-row 1 --end-row 1 --dry-run
node cli.js my-request-get-my-requests --help
```

### cartable-get-cartable-requests

نام‌های کوتاه: `cartable`

```powershell
node cli.js cartable-get-cartable-requests --client-id null --description null --from-expire-date null --from-request-date null --load-approval false --operational false --priority null --request-code null --request-type null --status null --to-expire-date null --to-request-date null --start-row null --end-row null --dry-run
node cli.js cartable-get-cartable-requests --help
```

### general-get-card-and-deposit-with-amount

نام‌های کوتاه: `accounts-with-cards`

```powershell
node cli.js general-get-card-and-deposit-with-amount --dry-run
node cli.js general-get-card-and-deposit-with-amount --help
```

### general-get-home-page-services

نام‌های کوتاه: `home`

```powershell
node cli.js general-get-home-page-services --dry-run
node cli.js general-get-home-page-services --help
```

### wallet-token-exchange

نام‌های کوتاه: `wallet-token`

```powershell
node cli.js wallet-token-exchange --response-type YOUR_VALUE --service-access-category-type YOUR_VALUE --dry-run
node cli.js wallet-token-exchange --help
```

### general-get-banners-by-mode

نام‌های کوتاه: `banners`

```powershell
node cli.js general-get-banners-by-mode --banner-mode YOUR_VALUE --dry-run
node cli.js general-get-banners-by-mode --help
```

### general-get-bottom-tab-menus

نام‌های کوتاه: `menus`

```powershell
node cli.js general-get-bottom-tab-menus --dry-run
node cli.js general-get-bottom-tab-menus --help
```

### inquiry-get-account-balance

نام‌های کوتاه: `balance`، `account-balance`

```powershell
node cli.js inquiry-get-account-balance --account-number YOUR_VALUE --dry-run
node cli.js inquiry-get-account-balance --help
```

### inquiry-get-modern-gateway-new-service-limitation

نام‌های کوتاه: `transfer-limits`

```powershell
node cli.js inquiry-get-modern-gateway-new-service-limitation --activity-type null --customer-number YOUR_VALUE --dry-run
node cli.js inquiry-get-modern-gateway-new-service-limitation --help
```

### workflow-cancel-instance

نام‌های کوتاه: `workflow-cancel`

```powershell
node cli.js workflow-cancel-instance --workflow-instance-id YOUR_VALUE --dry-run
node cli.js workflow-cancel-instance --help
```

### inquiry-get-card-owner-without-login

نام‌های کوتاه: `card-owner`

```powershell
node cli.js inquiry-get-card-owner-without-login --card-authorize-params.cvv2 YOUR_VALUE --card-authorize-params.exp-date YOUR_VALUE --card-authorize-params.pin YOUR_VALUE --card-authorize-params.pin-type 1 --card-authorize-params.track2 YOUR_VALUE --destination-pan YOUR_VALUE --pan YOUR_VALUE --dry-run
node cli.js inquiry-get-card-owner-without-login --help
```

### inquiry-get-iban-from-card

نام‌های کوتاه: `card-iban`، `iban`

```powershell
node cli.js inquiry-get-iban-from-card --card-number YOUR_VALUE --dry-run
node cli.js inquiry-get-iban-from-card --help
```

### general-get-transmission-method

نام‌های کوتاه: `transfer-methods`

```powershell
node cli.js general-get-transmission-method --amount 1 --destination-no YOUR_VALUE --mobile-step YOUR_VALUE --source-no YOUR_VALUE --dry-run
node cli.js general-get-transmission-method --help
```

### workflow-create-and-execute

نام‌های کوتاه: `workflow-create`

```powershell
node cli.js workflow-create-and-execute --name YOUR_VALUE --user-id YOUR_VALUE --dry-run
node cli.js workflow-create-and-execute --help
```

### workflow-inquiry-state

نام‌های کوتاه: `workflow-state`

```powershell
node cli.js workflow-inquiry-state --workflow-instance-id YOUR_VALUE --dry-run
node cli.js workflow-inquiry-state --help
```

### workflow-publish-event

نام‌های کوتاه: `workflow-event`

```powershell
node cli.js workflow-publish-event --event-data.action-type YOUR_VALUE --event-data.transfer-type YOUR_VALUE --event-data.card-transfer-data.amount YOUR_VALUE --event-data.card-transfer-data.contact-destination.data YOUR_VALUE --event-data.card-transfer-data.contact-destination.type YOUR_VALUE --event-data.card-transfer-data.deposit YOUR_VALUE --event-data.card-transfer-data.des YOUR_VALUE --event-data.card-transfer-data.iban YOUR_VALUE --event-data.card-transfer-data.isme false --event-data.card-transfer-data.main-account YOUR_VALUE --event-data.card-transfer-data.method YOUR_VALUE --event-data.card-transfer-data.month YOUR_VALUE --event-data.card-transfer-data.name YOUR_VALUE --event-data.card-transfer-data.pan YOUR_VALUE --event-data.card-transfer-data.parsian-data.data YOUR_VALUE --event-data.card-transfer-data.parsian-data.type YOUR_VALUE --event-data.card-transfer-data.payment-code YOUR_VALUE --event-data.card-transfer-data.receiver YOUR_VALUE --event-data.card-transfer-data.receiver-first-name YOUR_VALUE --event-data.card-transfer-data.receiver-last-name YOUR_VALUE --event-data.card-transfer-data.sender-description YOUR_VALUE --event-data.card-transfer-data.step2 YOUR_VALUE --event-data.card-transfer-data.switch-response-rrn YOUR_VALUE --event-data.card-transfer-data.transaction-date YOUR_VALUE --event-data.card-transfer-data.transaction-number YOUR_VALUE --event-data.card-transfer-data.transfer-fee YOUR_VALUE --event-data.card-transfer-data.year YOUR_VALUE --event-data.date-transaction YOUR_VALUE --event-name YOUR_VALUE --workflow-instance-id YOUR_VALUE --dry-run
node cli.js workflow-publish-event --help
```

### otp-get-offline-password-status

نام‌های کوتاه: `card-password-status`

```powershell
node cli.js otp-get-offline-password-status --card-number YOUR_VALUE --dry-run
node cli.js otp-get-offline-password-status --help
```

### otp-shetab-otp-sms-v2

نام‌های کوتاه: `transfer-otp`، `card-otp`

```powershell
node cli.js otp-shetab-otp-sms-v2 --pan YOUR_VALUE --amount 1 --transaction-type YOUR_VALUE --tracking-number YOUR_VALUE --card-acceptor-name YOUR_VALUE --payee YOUR_VALUE --dry-run
node cli.js otp-shetab-otp-sms-v2 --help
```

### transfer-card-transfer-without-login

نام‌های کوتاه: `transfer-card`

```powershell
node cli.js transfer-card-transfer-without-login --amount 1 --cvv2 YOUR_VALUE --destination YOUR_VALUE --destination-type YOUR_VALUE --exp-date YOUR_VALUE --pan YOUR_VALUE --pin YOUR_VALUE --pin-type YOUR_VALUE --transaction-number YOUR_VALUE --mobile-no YOUR_VALUE --is-save-to-contact false --sender-description null --receiver-description null --first-name YOUR_VALUE --last-name YOUR_VALUE --dry-run
node cli.js transfer-card-transfer-without-login --help
```

### inquiry-iban-enquiry

نام‌های کوتاه: `iban-inquiry`، `owner`

```powershell
node cli.js inquiry-iban-enquiry --iban YOUR_VALUE --dry-run
node cli.js inquiry-iban-enquiry --help
```

### payment-payment-idcheck-by-cb

نام‌های کوتاه: `payment-id-check`

```powershell
node cli.js payment-payment-idcheck-by-cb --applicant-bic-code null --iban YOUR_VALUE --payment-id YOUR_VALUE --amount 1 --dry-run
node cli.js payment-payment-idcheck-by-cb --help
```

### general-load-general-parameter

نام‌های کوتاه: `parameters`

```powershell
node cli.js general-load-general-parameter --code YOUR_VALUE --is-active false --dry-run
node cli.js general-load-general-parameter --help
```

### inquiry-sayah-system-compatibility-inquiry

نام‌های کوتاه: `sayah-inquiry`

```powershell
node cli.js inquiry-sayah-system-compatibility-inquiry --source-account-external-ref YOUR_VALUE --destination-account-external-ref null --destination-sheba-id YOUR_VALUE --dry-run
node cli.js inquiry-sayah-system-compatibility-inquiry --help
```

### otp-otp-generate-for-account-transfer

نام‌های کوتاه: `transfer-instant-otp`، `transfer-iban-otp`، `account-transfer-otp`، `transfer-instant-sms-request`، `transfer-iban-sms-request`، `pol-code`، `sheba-code`

```powershell
node cli.js otp-otp-generate-for-account-transfer --account-number YOUR_VALUE --amount 1 --ch-account-transfer-type YOUR_VALUE --ch-channel-type YOUR_VALUE --customer-number YOUR_VALUE --username YOUR_VALUE --destination-number YOUR_VALUE --dry-run
node cli.js otp-otp-generate-for-account-transfer --help
```

### transfer-post-payment-order

نام‌های کوتاه: `transfer-order`، `transfer-instant`، `transfer-iban`، `transfer-instant-fixed`، `transfer-instant-sms`، `pol`، `pol-sms`

```powershell
node cli.js transfer-post-payment-order --ch-payment-order-rq-bean.amount 1 --ch-payment-order-rq-bean.branch-code YOUR_VALUE --ch-payment-order-rq-bean.creditor-identification.iban YOUR_VALUE --ch-payment-order-rq-bean.creditor-identification.account-number null --ch-payment-order-rq-bean.creditor-identification.address-type-code null --ch-payment-order-rq-bean.debtor-identification.account-number YOUR_VALUE --ch-payment-order-rq-bean.debtor-identification.iban null --ch-payment-order-rq-bean.debtor-identification.address-type-code null --ch-payment-order-rq-bean.payment-purpose YOUR_VALUE --ch-second-password-type YOUR_VALUE --transfer-description YOUR_VALUE --second-password YOUR_VALUE --first-name YOUR_VALUE --last-name YOUR_VALUE --is-save-to-contact false --payment-code YOUR_VALUE --post-payment-order YOUR_VALUE --dry-run
node cli.js transfer-post-payment-order --help
```

### report-get-payment-order

نام‌های کوتاه: `payment-orders`

```powershell
node cli.js report-get-payment-order --ch-payment-order-param-bean.amount null --ch-payment-order-param-bean.branch-code null --ch-payment-order-param-bean.cbi-result null --ch-payment-order-param-bean.creditor-bank-id null --ch-payment-order-param-bean.creditor-iban null --ch-payment-order-param-bean.creditor-identification-id null --ch-payment-order-param-bean.creditor-shahab-code null --ch-payment-order-param-bean.debtor-account-numbers YOUR_VALUE --ch-payment-order-param-bean.debtor-bank-id null --ch-payment-order-param-bean.debtor-iban null --ch-payment-order-param-bean.debtor-identification-id null --ch-payment-order-param-bean.debtor-shahab-code null --ch-payment-order-param-bean.from-amount null --ch-payment-order-param-bean.from-submit-time YOUR_VALUE --ch-payment-order-param-bean.id null --ch-payment-order-param-bean.message-id null --ch-payment-order-param-bean.name null --ch-payment-order-param-bean.page YOUR_VALUE --ch-payment-order-param-bean.payment-code null --ch-payment-order-param-bean.persian-working-date null --ch-payment-order-param-bean.pp-name null --ch-payment-order-param-bean.remittance-information-structured null --ch-payment-order-param-bean.remittance-information-unstructured null --ch-payment-order-param-bean.reversed null --ch-payment-order-param-bean.send-to-cbi-time null --ch-payment-order-param-bean.settled-date-time null --ch-payment-order-param-bean.size YOUR_VALUE --ch-payment-order-param-bean.status-code null --ch-payment-order-param-bean.submit-time null --ch-payment-order-param-bean.to-amount null --ch-payment-order-param-bean.to-submit-time YOUR_VALUE --ch-payment-order-param-bean.tracking-code YOUR_VALUE --ch-payment-order-param-bean.transaction-id null --dry-run
node cli.js report-get-payment-order --help
```

### transfer-ach-normal-transfer

نام‌های کوتاه: `transfer-ach`، `transfer-iban-fixed`، `transfer-iban-sms`، `sheba`، `sheba-sms`

```powershell
node cli.js transfer-ach-normal-transfer --amount 1 --check-unique-tracking-code false --source-deposit-number YOUR_VALUE --iban-number YOUR_VALUE --ch-second-password-type YOUR_VALUE --unique-tracking-code YOUR_VALUE --second-password YOUR_VALUE --owner-name YOUR_VALUE --first-name YOUR_VALUE --last-name YOUR_VALUE --email YOUR_VALUE --factor-number YOUR_VALUE --transfer-description YOUR_VALUE --description YOUR_VALUE --reason YOUR_VALUE --is-save-to-contact false --dry-run
node cli.js transfer-ach-normal-transfer --help
```

### inquiry-get-statement

نام‌های کوتاه: `transactions`

```powershell
node cli.js inquiry-get-statement --deposit-number YOUR_VALUE --action null --length 1 --offset 1 --description YOUR_VALUE --from-date YOUR_VALUE --to-date YOUR_VALUE --order YOUR_VALUE --customer-description YOUR_VALUE --ch-statement-search-direction YOUR_VALUE --from-amount null --to-amount null --type-transaction null --dry-run
node cli.js inquiry-get-statement --help
```

### inquiry-get-min-balance-average

نام‌های کوتاه: `balance-average`

```powershell
node cli.js inquiry-get-min-balance-average --external-ref-list YOUR_VALUE --from-date YOUR_VALUE --to-date YOUR_VALUE --dry-run
node cli.js inquiry-get-min-balance-average --help
```

### receipt-get-next-bank-receipt-by-statement-by-id

نام‌های کوتاه: `receipt`، `transaction`

```powershell
node cli.js receipt-get-next-bank-receipt-by-statement-by-id --statement-id YOUR_ID --dry-run
node cli.js receipt-get-next-bank-receipt-by-statement-by-id --help
```

### inquiry-ach-transfer-full-report

نام‌های کوتاه: `transfer-report`

```powershell
node cli.js inquiry-ach-transfer-full-report --cif null --client-tracking-code null --description null --destination-iban-number null --destination-owner-name null --factor-number null --from-issue-date null --from-register-date YOUR_VALUE --from-transaction-amount null --length 1 --offset 1 --order YOUR_VALUE --reference-id null --source-deposit-iban null --source-deposit-number YOUR_VALUE --status-set null --to-issue-date null --to-register-date YOUR_VALUE --to-transaction-amount null --transaction-status-set null --transfer-description null --dry-run
node cli.js inquiry-ach-transfer-full-report --help
```

### receipt-get-next-bank-receipts

نام‌های کوتاه: `receipts`

```powershell
node cli.js receipt-get-next-bank-receipts --from-date YOUR_VALUE --to-date YOUR_VALUE --page-number 1 --page-size 1 --receipt-keyword null --from-amount null --to-amount null --dry-run
node cli.js receipt-get-next-bank-receipts --help
```

### general-handle-customer-config-and-detail

نام‌های کوتاه: `config-save`

```powershell
node cli.js general-handle-customer-config-and-detail --0.key YOUR_VALUE --0.value YOUR_VALUE --0.type YOUR_VALUE --dry-run
node cli.js general-handle-customer-config-and-detail --help
```

### general-get-service-page-services

نام‌های کوتاه: `services`

```powershell
node cli.js general-get-service-page-services --dry-run
node cli.js general-get-service-page-services --help
```

### card-get-customer-account-and-card

نام‌های کوتاه: `customer-cards`

```powershell
node cli.js card-get-customer-account-and-card --dry-run
node cli.js card-get-customer-account-and-card --help
```

### general-get-customer-config-detail-by-cif-with-out-session

نام‌های کوتاه: `customer-config-public`

```powershell
node cli.js general-get-customer-config-detail-by-cif-with-out-session --cif YOUR_VALUE --dry-run
node cli.js general-get-customer-config-detail-by-cif-with-out-session --help
```

### workflow-get-latest-active-instance

نام‌های کوتاه: `workflow-latest`

```powershell
node cli.js workflow-get-latest-active-instance --workflow-name YOUR_VALUE --dry-run
node cli.js workflow-get-latest-active-instance --help
```

</details>

## نگاشت CLI و API

| فرمان | مسیر HTTP |
| --- | --- |
| `customer-config-public` | `POST /v1/customer/config` |
| `workflow-latest` | `POST /v1/workflow/latest` |
| `transfer-instant` | `POST /v1/transfers/instant` |
| `transfer-instant-otp` | `POST /v1/transfers/instant/otp` |
| `transfer-iban-otp` | `POST /v1/transfers/iban/otp` |
| `transfer-order` | `POST /v1/transfers/order` |
| `validate-mobile` | `POST /v1/auth/mobile/validate` |
| `otp-request` | `POST /v1/auth/otp/request` |
| `otp` | `POST /v1/auth/otp` |
| `login` | `POST /v1/auth/login` |
| `cards` | `GET /v1/cards` |
| `accounts` | `GET /v1/accounts` |
| `profile` | `POST /v1/profile` |
| `config` | `GET /v1/config` |
| `contacts` | `GET /v1/contacts` |
| `workflow-active` | `GET /v1/workflow/active` |
| `requests` | `POST /v1/requests` |
| `cartable` | `POST /v1/cartable` |
| `accounts-with-cards` | `GET /v1/accounts/with-cards` |
| `home` | `GET /v1/home` |
| `wallet-token` | `POST /v1/wallet/token` |
| `banners` | `GET /v1/banners` |
| `menus` | `GET /v1/menus` |
| `account-balance` | `GET /v1/accounts/{number}/balance` |
| `transfer-limits` | `POST /v1/transfers/limits` |
| `workflow-cancel` | `POST /v1/workflow/cancel` |
| `card-owner` | `POST /v1/transfers/card/owner` |
| `iban` | `GET /v1/cards/{number}/iban` |
| `transfer-methods` | `POST /v1/transfers/methods` |
| `workflow-create` | `POST /v1/workflow/create` |
| `workflow-state` | `POST /v1/workflow/state` |
| `workflow-event` | `POST /v1/workflow/event` |
| `card-password-status` | `POST /v1/cards/password/status` |
| `transfer-otp` | `POST /v1/transfers/card/otp` |
| `transfer-card` | `POST /v1/transfers/card` |
| `owner` | `GET /v1/owner/iban/{iban}` |
| `payment-id-check` | `POST /v1/payments/id/check` |
| `parameters` | `POST /v1/parameters` |
| `sayah-inquiry` | `POST /v1/transfers/sayah` |
| `account-transfer-otp` | `POST /v1/transfers/account/otp` |
| `transfer-iban` | `POST /v1/transfers/iban` |
| `payment-orders` | `POST /v1/reports/payment-orders` |
| `transfer-ach` | `POST /v1/transfers/ach` |
| `transactions` | `GET /v1/transactions` |
| `balance-average` | `POST /v1/balances/average` |
| `transaction` | `GET /v1/transactions/{id}` |
| `transfer-report` | `POST /v1/reports/transfers` |
| `receipts` | `POST /v1/receipts` |
| `config-save` | `POST /v1/config` |
| `services` | `GET /v1/services` |
| `customer-cards` | `GET /v1/customer/cards` |
| `transfer-instant-fixed` | `POST /v1/transfers/fixed/instant` |
| `transfer-iban-fixed` | `POST /v1/transfers/fixed/iban` |
| `transfer-instant-sms-request` | `POST /v1/transfers/sms/instant/otp` |
| `transfer-instant-sms` | `POST /v1/transfers/sms/instant` |
| `transfer-iban-sms-request` | `POST /v1/transfers/sms/iban/otp` |
| `transfer-iban-sms` | `POST /v1/transfers/sms/iban` |
| `pol` | `POST /v1/pol` |
| `sheba` | `POST /v1/sheba` |
| `pol-sms` | `POST /v1/pol/sms` |
| `sheba-sms` | `POST /v1/sheba/sms` |
| `pol-code` | `POST /v1/pol/code` |
| `sheba-code` | `POST /v1/sheba/code` |
| `status` | `GET /v1/auth/session` |
| `check-session` | `POST /v1/auth/session/check` |
| `ensure-session` | `POST /v1/auth/session/ensure` |
| `logout` | `POST /v1/auth/logout` |
| `deposits` | `GET /v1/deposits` |
| `cards-all` | `GET /v1/cards/all` |
| `deposits-all` | `GET /v1/deposits/all` |
| `balance` | `GET /v1/balance` |
| `balance-cards` | `GET /v1/balances/cards` |
| `balance-deposits` | `GET /v1/balances/deposits` |
| `transactions-latest` | `GET /v1/transactions/latest` |
| `transaction-find` | `GET /v1/transactions/find/{code}` |


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


## انتقال‌های عمومی و کارت‌به‌کارت

```powershell
node cli.js card-owner --pan YOUR_SOURCE_CARD --destination-pan YOUR_DEST_CARD
node cli.js transfer-otp YOUR_SOURCE_CARD YOUR_DEST_CARD 10000 --tracking-number YOUR_OTP_TRACKING
node cli.js transfer-card YOUR_SOURCE_CARD YOUR_DEST_CARD 10000 --cvv2 YOUR_CVV2 --expiry YYMM --transaction-number YOUR_TRANSACTION_NUMBER --mobile-number YOUR_MOBILE
```

رمز کارت مخفی پرسیده می‌شود. transactionNumber را از استعلام صاحب کارت دریافت کنید؛ trackingNumber درخواست رمز شناسه جداگانه‌ای است. expiry قالب YYMM دارد.

```powershell
node cli.js transfer-instant YOUR_ACCOUNT YOUR_IBAN 10000 --password-mode fixed --reason LMAP --branch-code YOUR_BRANCH
node cli.js transfer-iban YOUR_ACCOUNT YOUR_IBAN 10000 --password-mode sms --reason LMAP
```

برای روش مشخص، فرمان‌های دو بخش مستقل بالا ساده‌ترند. مراحل Workflow نیز با فرمان‌های workflow-create، workflow-state و workflow-event و فیلدهای --Name، --UserId، --WorkflowInstanceId، --EventName و --EventData.parent.child در دسترس‌اند. برنامه رویدادها را خودکار منتشر نمی‌کند. درخواست OTP و انتقال جدا هستند؛ با اجرای فرمان واقعی عملیات ثبت می‌شود و تأیید تعاملی جداگانه ندارد. تمام آزمون‌های انتقال این نسخه شبیه‌سازی‌شده‌اند.


## دریافت فایل‌ها

- [OpenAPI سرویس محلی](/parsian/downloads/openapi.json)
- [Postman سرویس محلی](/parsian/downloads/parsian-api.postman_collection.json)
- [مرجع کامل فارسی](/parsian/downloads/API-REFERENCE.fa.md)

Postman از baseUrl محلی با /v1 و apiKey استفاده می‌کند. مقادیر نمونه را جایگزین کنید. نشست و فایل HAR منتشر نمی‌شوند.

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


## POST /customer/config

این مسیر محلی به POST /api/General/GetCustomerConfigDetailByCifWithOutSession بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `cif`

فرمان: customer-config-public


## POST /workflow/latest

این مسیر محلی به POST /api/Workflow/GetLatestActiveInstance بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `WorkflowName`

فرمان: workflow-latest


## POST /transfers/instant

پل/Instant با PostPaymentOrder و هر دو حالت sms و fixed. 

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-instant


## POST /transfers/instant/otp

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `customerNumber`، `username`

فرمان: transfer-instant-otp


## POST /transfers/iban/otp

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `customerNumber`، `username`

فرمان: transfer-iban-otp


## POST /transfers/order

این مسیر محلی به POST /api/Transfer/PostPaymentOrder بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `chPaymentOrderRqBean`، `chSecondPasswordType`، `transferDescription`، `secondPassword`، `firstName`، `lastName`، `isSaveToContact`، `paymentCode`، `postPaymentOrder`

فرمان: transfer-order


## POST /auth/mobile/validate

این مسیر محلی به POST /api/General/ValidateWhitelistedUser بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `mobileNumber`، `versionNumber`

فرمان: validate-mobile


## POST /auth/otp/request

این مسیر محلی به POST /api/Otp/OtpGeneratorWithMobileNo بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `mobileNo`

فرمان: otp-request


## POST /auth/otp

این مسیر محلی به POST /api/Otp/ValidateMobileNoWithOtp بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `mobileNo`، `signedPassword`

فرمان: otp


## POST /auth/login

این مسیر محلی به POST /api/User/Login بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `additionalData`، `mobileNumber`، `password`، `username`

فرمان: login


## GET /cards

این مسیر محلی به POST /api/Inquiry/GetCardsWithAmount بانک پارسیان وصل است. 16 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: cards


## GET /accounts

این مسیر محلی به POST /api/Inquiry/GetDeposits بانک پارسیان وصل است. 15 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: accounts


## POST /profile

این مسیر محلی به POST /api/Inquiry/GetCustomerExtraData بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `cif`

فرمان: profile


## GET /config

این مسیر محلی به GET /api/General/GetCustomerConfigDetailByCif بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: config


## POST /config

این مسیر محلی به POST /api/General/HandleCustomerConfigAndDetail بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: config-save


## GET /contacts

این مسیر محلی به POST /api/Inquiry/GetUserContactWithContactDetails بانک پارسیان وصل است. 14 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: contacts


## GET /workflow/active

این مسیر محلی به POST /api/Workflow/GetActiveInstances بانک پارسیان وصل است. 7 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: workflow-active


## POST /requests

این مسیر محلی به POST /api/MyRequest/GetMyRequests بانک پارسیان وصل است. 7 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `requestType`، `requestCode`، `status`، `fromRequestDate`، `toRequestDate`، `fromExpireDate`، `toExpireDate`، `priority`، `operational`، `loadApproval`، `clientId`، `description`، `startRow`، `endRow`

فرمان: requests


## POST /cartable

این مسیر محلی به POST /api/Cartable/GetCartableRequests بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `clientId`، `description`، `fromExpireDate`، `fromRequestDate`، `loadApproval`، `operational`، `priority`، `requestCode`، `requestType`، `status`، `toExpireDate`، `toRequestDate`، `startRow`، `endRow`

فرمان: cartable


## GET /accounts/with-cards

این مسیر محلی به GET /api/General/GetCardAndDepositWithAmount/ بانک پارسیان وصل است. 15 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: accounts-with-cards


## GET /home

این مسیر محلی به GET /api/General/GetHomePageServices بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: home


## POST /wallet/token

این مسیر محلی به POST /api/Wallet/TokenExchange بانک پارسیان وصل است. 16 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `responseType`، `serviceAccessCategoryType`

فرمان: wallet-token


## GET /banners

این مسیر محلی به GET /api/General/GetBannersByMode بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: banners


## GET /menus

این مسیر محلی به GET /api/General/GetBottomTabMenus بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: menus


## GET /accounts/{number}/balance

این مسیر محلی به POST /api/Inquiry/GetAccountBalance بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: account-balance


## POST /transfers/limits

این مسیر محلی به POST /api/Inquiry/GetModernGatewayNewServiceLimitation بانک پارسیان وصل است. 12 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `activityType`، `customerNumber`

فرمان: transfer-limits


## POST /workflow/cancel

این مسیر محلی به POST /api/Workflow/CancelInstance بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `WorkflowInstanceId`

فرمان: workflow-cancel


## POST /transfers/card/owner

این مسیر محلی به POST /api/Inquiry/GetCardOwnerWithoutLogin بانک پارسیان وصل است. 12 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `cardAuthorizeParams`، `destinationPan`، `pan`

فرمان: card-owner


## GET /cards/{number}/iban

این مسیر محلی به POST /api/Inquiry/GetIbanFromCard بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: iban


## POST /transfers/methods

این مسیر محلی به POST /api/General/GetTransmissionMethod بانک پارسیان وصل است. 12 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `amount`، `destinationNo`، `mobileStep`، `sourceNo`

فرمان: transfer-methods


## POST /workflow/create

این مسیر محلی به POST /api/Workflow/createAndExecute بانک پارسیان وصل است. 11 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `Name`، `UserId`

فرمان: workflow-create


## POST /workflow/state

این مسیر محلی به POST /api/Workflow/InquiryState بانک پارسیان وصل است. 11 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `WorkflowInstanceId`

فرمان: workflow-state


## POST /workflow/event

این مسیر محلی به POST /api/Workflow/PublishEvent بانک پارسیان وصل است. 22 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `EventData`، `EventName`، `WorkflowInstanceId`

فرمان: workflow-event


## POST /cards/password/status

این مسیر محلی به POST /api/otp/GetOfflinePasswordStatus بانک پارسیان وصل است. 2 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `CardNumber`

فرمان: card-password-status


## POST /transfers/card/otp

این مسیر محلی به POST /api/Otp/ShetabOtpSmsV2 بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceCard`، `destinationCard`، `amount`، `trackingNumber`، `cardAcceptorName`

فرمان: transfer-otp


## POST /transfers/card

این مسیر محلی به POST /api/Transfer/CardTransferWithoutLogin بانک پارسیان وصل است. 3 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceCard`، `destinationCard`، `amount`، `passwordMode`، `password`، `cvv2`، `expiry`، `transactionNumber`، `trackingNumber`، `mobileNumber`، `firstName`، `lastName`، `senderDescription`، `receiverDescription`، `isSaveToContact`، `cardAcceptorName`

فرمان: transfer-card


## GET /owner/iban/{iban}

این مسیر محلی به POST /api/Inquiry/IbanEnquiry بانک پارسیان وصل است. 26 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: owner


## POST /payments/id/check

این مسیر محلی به POST /api/payment/PaymentIDCheckByCB بانک پارسیان وصل است. 2 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `applicantBicCode`، `iban`، `paymentID`، `amount`

فرمان: payment-id-check


## POST /parameters

این مسیر محلی به POST /api/General/LoadGeneralParameter بانک پارسیان وصل است. 2 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `code`، `isActive`

فرمان: parameters


## POST /transfers/sayah

این مسیر محلی به POST /api/Inquiry/SayahSystemCompatibilityInquiry بانک پارسیان وصل است. 2 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccountExternalRef`، `destinationAccountExternalRef`، `destinationShebaId`

فرمان: sayah-inquiry


## POST /transfers/account/otp

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `customerNumber`، `username`

فرمان: account-transfer-otp


## POST /transfers/iban

ورودی ساده به AchNormalTransfer برای شبا/پایا می‌رود؛ بدنه خام قدیمی chPaymentOrderRqBean همچنان به PostPaymentOrder برای پل می‌رود. 

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-iban


## POST /reports/payment-orders

این مسیر محلی به POST /api/Report/GetPaymentOrder بانک پارسیان وصل است. 5 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `chPaymentOrderParamBean`

فرمان: payment-orders


## POST /transfers/ach

این مسیر محلی به POST /api/Transfer/AchNormalTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-ach


## GET /transactions

این مسیر محلی به POST /api/Inquiry/GetStatement بانک پارسیان وصل است. 14 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: transactions


## POST /balances/average

این مسیر محلی به POST /api/Inquiry/GetMinBalanceAverage بانک پارسیان وصل است. 12 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `externalRefList`، `fromDate`، `toDate`

فرمان: balance-average


## GET /transactions/{id}

این مسیر محلی به GET /api/Receipt/GetNextBankReceiptByStatement/{statementId} بانک پارسیان وصل است. 5 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: transaction


## POST /reports/transfers

این مسیر محلی به POST /api/Inquiry/AchTransferFullReport بانک پارسیان وصل است. 2 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `cif`، `clientTrackingCode`، `description`، `destinationIbanNumber`، `destinationOwnerName`، `factorNumber`، `fromIssueDate`، `fromRegisterDate`، `fromTransactionAmount`، `length`، `offset`، `order`، `referenceId`، `sourceDepositIban`، `sourceDepositNumber`، `statusSet`، `toIssueDate`، `toRegisterDate`، `toTransactionAmount`، `transactionStatusSet`، `transferDescription`

فرمان: transfer-report


## POST /receipts

این مسیر محلی به POST /api/Receipt/GetNextBankReceipts بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `fromDate`، `toDate`، `pageNumber`، `pageSize`، `ReceiptKeyword`، `FromAmount`، `ToAmount`

فرمان: receipts


## GET /services

این مسیر محلی به GET /api/General/GetServicePageServices بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: services


## GET /customer/cards

این مسیر محلی به POST /api/card/getCustomerAccountAndCard بانک پارسیان وصل است. 1 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: 

فرمان: customer-cards


## POST /transfers/fixed/instant

این مسیر محلی به POST /api/Transfer/PostPaymentOrder بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-instant-fixed


## POST /transfers/fixed/iban

این مسیر محلی به POST /api/Transfer/AchNormalTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-iban-fixed


## POST /transfers/sms/instant/otp

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `customerNumber`، `username`، `passwordMode`

فرمان: transfer-instant-sms-request


## POST /transfers/sms/instant

این مسیر محلی به POST /api/Transfer/PostPaymentOrder بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-instant-sms


## POST /transfers/sms/iban/otp

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `customerNumber`، `username`، `passwordMode`

فرمان: transfer-iban-sms-request


## POST /transfers/sms/iban

این مسیر محلی به POST /api/Transfer/AchNormalTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `sourceAccount`، `iban`، `amount`، `passwordMode`، `password`، `reason`، `branchCode`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: transfer-iban-sms


## POST /pol

این مسیر محلی به POST /api/Transfer/PostPaymentOrder بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `from`، `to`، `amount`، `passwordMode`، `pass`، `reason`، `branch`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: pol


## POST /sheba

این مسیر محلی به POST /api/Transfer/AchNormalTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `from`، `to`، `amount`، `passwordMode`، `pass`، `reason`، `branch`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: sheba


## POST /pol/sms

این مسیر محلی به POST /api/Transfer/PostPaymentOrder بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `from`، `to`، `amount`، `passwordMode`، `pass`، `reason`، `branch`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: pol-sms


## POST /sheba/sms

این مسیر محلی به POST /api/Transfer/AchNormalTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `from`، `to`، `amount`، `passwordMode`، `pass`، `reason`، `branch`، `firstName`، `lastName`، `ownerName`، `transferDescription`، `description`، `paymentCode`، `isSaveToContact`

فرمان: sheba-sms


## POST /pol/code

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `from`، `to`، `amount`، `customer`، `user`، `passwordMode`

فرمان: pol-code


## POST /sheba/code

این مسیر محلی به POST /api/Otp/OtpGenerateForAccountTransfer بانک پارسیان وصل است. 4 نمونه در HAR ثبت شده؛ قرارداد ورودی از ضبط گرفته شده است.

فیلدها: `from`، `to`، `amount`، `customer`، `user`، `passwordMode`

فرمان: sheba-code


## GET /auth/session

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: status


## POST /auth/session/check

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: check-session


## POST /auth/session/ensure

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: ensure-session


## POST /auth/logout

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: logout


## GET /deposits

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: deposits


## GET /cards/all

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: cards-all


## GET /deposits/all

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: deposits-all


## GET /balance

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: balance


## GET /balances/cards

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: balance-cards


## GET /balances/deposits

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: balance-deposits


## GET /transactions/latest

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: transactions-latest


## GET /transactions/find/{code}

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: transaction-find


## GET /health

عملیات محلی یا تجمیعی نشست و داده‌های پارسیان.

فیلدها: 

فرمان: health
