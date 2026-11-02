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
