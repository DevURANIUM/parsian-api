# انتشار GitHub و PyPI

این راهنما برای مخزن https://github.com/DevURANIUM/parsian-api آماده شده است.
سورس Node و Python در یک مخزن قرار می‌گیرند؛ بسته PyPI فقط کتابخانه پایتون را نصب می‌کند.
نسخه اولیه Python برابر 0.1.0 است و مستقل از نسخه سرویس 0.5.0 منتشر می‌شود.

## تنظیمات Trusted Publisher

همان مقادیر فرم PyPI را وارد کنید:

| فیلد | مقدار دقیق |
| --- | --- |
| PyPI Project Name | parsian-api |
| Owner | DevURANIUM |
| Repository name | parsian-api |
| Workflow name | workflow.yml |
| Environment name | pypi |

در GitHub، Settings → Environments یک محیط با نام pypi بسازید.
در PyPI، Pending Publisher یا Trusted Publisher را با مقادیر بالا ثبت کنید.
فایل مربوطه در .github/workflows/workflow.yml است. نام workflow در فرم، نام همین فایل است، نه عنوان نمایشی Action.
توکن PyPI در کد، فایل env یا GitHub Secret لازم نیست؛ workflow از OIDC استفاده می‌کند.

راهنمای رسمی: https://docs.pypi.org/trusted-publishers/adding-a-publisher/

## آپلود سورس آماده

اگر نسخه تمیز را از پوشه release پروژه می‌فرستید، ابتدا مخزن موجود را clone کنید تا تاریخچه اولیه آن حفظ شود.
از ساخت تاریخچه جدید و push اجباری استفاده نکنید.

```powershell
git clone https://github.com/DevURANIUM/parsian-api.git parsian-api-publish
```

محتویات پوشه تمیز release/parsian-api را داخل parsian-api-publish کپی کنید؛ خود پوشه release را کپی نکنید.
فایل‌های نقطه‌دار .github و .gitignore و .env.example نیز باید منتقل شوند. سپس:

```powershell
cd parsian-api-publish
git status --short
git add .
git commit -m "feat: add Parsian API and Python SDK"
git push origin main
```

فایل واقعی .env، data/session.json، HARها، research، reports و پوشه مجازی پایتون نباید در تغییرات Git دیده شوند.
نسخه تمیز انتشار فقط فایل نمونه .env.example دارد.

## تست پیش از انتشار

```powershell
npm ci
npm test
python -m pip install -e ./python pytest build twine
python -m pytest python/tests -q
python -m build python
python -m twine check python/dist/*
```

تست‌های مالی به بانک شبیه‌سازی‌شده وصل‌اند و پول یا پیامک واقعی ارسال نمی‌کنند.
فایل‌های wheel و tar.gz در python/dist ساخته می‌شوند؛ لازم نیست آن‌ها را در Git commit کنید.

## انتشار اولیه PyPI

بعد از سبز شدن CI و ذخیره تنظیمات Trusted Publisher، در GitHub وارد Actions شوید، Publish parsian-api to PyPI را انتخاب کنید و Run workflow را بزنید. شاخه main و version=0.1.0 را انتخاب کنید. تگ لازم نیست. با GitHub CLI هم می‌توانید اجرا کنید:

```powershell
gh workflow run workflow.yml --ref main -f version=0.1.0
```

Action با نام Publish parsian-api to PyPI اجرا می‌شود: تست Node و Python، کنترل نسخه انتخاب‌شده، ساخت بسته، کنترل metadata و سپس انتشار از environment=pypi.
پس از موفق شدن مرحله publish:

```powershell
python -m pip install parsian-api
parsian-api --help
```

پیش از اولین انتشار، از python -m pip install ./python یا wheel محلی استفاده کنید.

## انتشار بعدی

نسخه را در python/pyproject.toml و python/src/parsianapi/__init__.py بالا ببرید؛ بسته و تست‌ها را بازسازی کنید، commit و push کنید، سپس Run workflow را با همان نسخه جدید اجرا کنید.
PyPI نسخه قبلی را بازنویسی نمی‌کند؛ برای هر انتشار، نسخه تازه‌ای انتخاب کنید.

اگر خطای trusted publisher گرفتید، owner، repository، workflow.yml و environment=pypi باید دقیقاً با فرم PyPI یکی باشند.
اگر environment در GitHub نیاز به تأیید دارد، انتشار تا تأیید خودتان منتظر می‌ماند.
