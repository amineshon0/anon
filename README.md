<div align="center">

# 💌 Telegram Anonymous Messaging Bot
### ربات پیام‌رسان ناشناس تلگرام — شیک، سریع و حرفه‌ای

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/python--telegram--bot-v21+-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Lightweight-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## ✨ امکانات (Features)

- 🔗 **لینک ناشناس اختصاصی**: هر کاربر یک لینک منحصربه‌فرد می‌گیره و هر زمان بخواد می‌تونه لینکش رو عوض (ریست) کنه.
- 💬 **پاسخ‌دهی دوطرفه و راحت**: زیر هر پیام دکمه «پاسخ» وجود داره تا بدون لو رفتن هویت، مکالمه ادامه پیدا کنه.
- 📎 **پشتیبانی از انواع مدیا**: متن، عکس، ویس، ویدیو، موزیک، فایل، استیکر و ویدیو دایره‌ای (Video Note).
- 🚫 **سیستم مسدودسازی (Block/Unblock)**: جلوگیری از اسپم و افراد مزاحم با یک کلیک.
- 📝 **متن خوش‌آمدگویی سفارشی (Custom Bio)**: نمایش متن دلخواه شما برای کسانی که روی لینکتون کلیک می‌کنن.
- 🔕 **توقف موقت دریافت پیام**: امکان خاموش/روشن کردن دریافت پیام جدید از بخش تنظیمات.
- 📊 **آمار شخصی و پنل دو ادمینه**: مشاهده تعداد پیام‌های دریافتی، ارسالی و کاربران مسدود شده + دستور `/admin` با پشتیبانی از دو (یا چند) ادمین از طریق `ADMIN_IDS`.
- 🐳 **آماده برای اجرا با Docker**: راه‌اندازی روی سرور در کمتر از ۱ دقیقه.

---

## ☁️ اجرای رایگان بدون نیاز به سرور (با GitHub + Render)

چون گیتهاب فقط محل نگهداری کد است و ربات را ۲۴ ساعته روشن نگه نمی‌دارد، می‌توانی ربات را خیلی راحت و **رایگان** به **Render.com** وصل کنی (فایل `render.yaml` و سرور سلامت آماده داخل پروژه قرار دارد):

1. یک ریپازیتوری جدید در **GitHub** بساز و فایل‌های همین پروژه را داخلش آپلود (Push) کن.
2. وارد سایت [render.com](https://render.com) شو و با اکانت **GitHub** وارد شو.
3. روی **New +** و سپس **Blueprint** (یا **Web Service**) بزن و ریپازیتوری گیتهابت را انتخاب کن.
4. در بخش **Environment Variables** این دو مقدار را وارد کن:
   - `BOT_TOKEN`: توکن رباتت از `@BotFather`
   - `ADMIN_IDS`: آیدی عددی دو ادمین (با کاما جدا شده، مثلاً `111111111,222222222`)
5. روی **Deploy** بزن — رباتت بدون نیاز به هیچ سروری اجرا می‌شود! 🎉

> 💡 **نکته:** در پلن رایگان Render، اگر ۱۵ دقیقه درخواست HTTP نیاید سرویس به خواب می‌رود. برای بیدار نگه داشتن همیشگی، می‌توانی آدرس سایت Render را در یک سرویس رایگان مثل [UptimeRobot](https://uptimerobot.com) ثبت کنی تا هر ۵ دقیقه یک پینگ بفرستد.

---

## 🚀 راه‌اندازی سریع روی سیستم شخصی یا سرور (Quick Start)

### ۱. دریافت توکن ربات
1. در تلگرام به [@BotFather](https://t.me/BotFather) پیام بده.
2. دستور `/newbot` رو بفرست و نام و یوزرنیم رباتت رو انتخاب کن.
3. توکن دریافتی رو کپی کن.

### ۲. نصب و اجرا (روش معمولی)

```bash
# کلون کردن پروژه
git clone https://github.com/YOUR_USERNAME/telegram-anonymous-bot.git
cd telegram-anonymous-bot

# ساخت محیط مجازی (پیشنهادی)
python3 -m venv .venv
source .venv/bin/activate  # در ویندوز: .venv\Scripts\activate

# نصب پکیج‌ها
pip install -r requirements.txt

# تنظیم فایل .env
cp .env.example .env
# حالا فایل .env رو باز کن و BOT_TOKEN رو داخلش بذار

# اجرای ربات
python -m src.bot
```

### ۳. اجرا با Docker (پیشنهادی برای سرور)

```bash
cp .env.example .env
# توکن ربات رو در .env قرار بده
docker compose up -d --build
```

---

## 📁 ساختار پروژه (Project Structure)

```text
telegram-anonymous-bot/
├── src/
│   ├── __init__.py
│   ├── bot.py          # منطق اصلی ربات و هندلرها
│   ├── config.py       # خواندن تنظیمات از .env
│   ├── database.py     # مدیریت دیتابیس SQLite
│   ├── keyboards.py    # دکمه‌های شیشه‌ای (Inline Keyboards)
│   └── texts.py        # متن‌ها و قالب‌بندی پیام‌ها
├── .env.example        # نمونه فایل تنظیمات
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🤝 مشارکت (Contributing)
هرگونه پیشنهاد، گزارش باگ یا Pull Request با کمال میل پذیرفته می‌شه!

## 📄 لایسنس
این پروژه تحت لایسنس [MIT](LICENSE) منتشر شده است.
