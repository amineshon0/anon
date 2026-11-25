from html import escape


def welcome_home(name: str) -> str:
    safe_name = escape(name)
    return (
        f"✨ <b>سلام {safe_name} عزیز، خوش اومدی!</b>\n\n"
        "با این ربات می‌تونی لینک ناشناس اختصاصی خودت رو بسازی و در بیو اینستاگرام، "
        "تلگرام یا هرجای دیگه بذاری تا بقیه بدون اینکه هویتشون مشخص بشه برات پیام بفرستن "
        "و تو هم خیلی راحت جوابشون رو بدی.\n\n"
        "👇 از منوی زیر انتخاب کن:"
    )


def my_link_text(link: str, is_accepting: bool, custom_bio: str) -> str:
    status = "🟢 فعال (در حال دریافت پیام)" if is_accepting else "🔴 غیرفعال (متوقف شده)"
    bio_line = (
        f"\n📝 <b>متن خوش‌آمدگویی تو:</b>\n<blockquote>{escape(custom_bio)}</blockquote>"
        if custom_bio
        else ""
    )
    return (
        "🔗 <b>لینک ناشناس اختصاصی تو آماده است!</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"📡 <b>وضعیت دریافت پیام:</b> {status}"
        f"{bio_line}\n\n"
        "💡 <i>روی لینک بالا بزن تا کپی بشه و هرجا دوست داری به اشتراک بذار!</i>"
    )


def send_prompt_text(target_name: str, custom_bio: str = "") -> str:
    safe_name = escape(target_name)
    bio_block = (
        f"\n💬 <b>پیام {safe_name}:</b>\n<blockquote>{escape(custom_bio)}</blockquote>\n"
        if custom_bio
        else "\n"
    )
    return (
        f"✉️ <b>ارسال پیام ناشناس به {safe_name}</b>"
        f"{bio_block}\n"
        "هر حرفی تو دلت هست رو بنویس و بفرست! "
        "می‌تونی متن، عکس، ویس، ویدیو یا استیکر بفرستی.\n\n"
        "🔒 <i>هویت تو کاملاً مخفی می‌مونه.</i>"
    )


def reply_prompt_text() -> str:
    return (
        "💬 <b>ارسال پاسخ</b>\n\n"
        "پاسخت رو بنویس و بفرست (متن، عکس، ویس، ویدیو یا استیکر).\n"
        "پاسخ تو مستقیماً برای فرستنده ارسال می‌شه!"
    )


def incoming_message_header(is_reply: bool = False) -> str:
    if is_reply:
        return "💬 <b>یک پاسخ جدید دریافت کردی!</b>"
    return "💌 <b>یک پیام ناشناس جدید داری!</b>"


def incoming_text_card(text: str, is_reply: bool = False) -> str:
    header = incoming_message_header(is_reply=is_reply)
    return f"{header}\n\n<blockquote>{escape(text)}</blockquote>"


def message_sent_text(is_reply: bool = False) -> str:
    if is_reply:
        return "✅ <b>پاسخ تو با موفقیت ارسال شد!</b>"
    return (
        "✅ <b>پیام ناشناس تو با موفقیت ارسال شد!</b>\n\n"
        "هر وقت پاسخ بده، همین‌جا برات میاد. ✨"
    )


def settings_text(is_accepting: bool, custom_bio: str) -> str:
    status = "🟢 فعال" if is_accepting else "🔴 غیرفعال"
    bio_preview = escape(custom_bio) if custom_bio else "تنظیم نشده"
    return (
        "⚙️ <b>تنظیمات حساب کاربری</b>\n\n"
        f"• <b>دریافت پیام جدید:</b> {status}\n"
        f"• <b>متن خوش‌آمدگویی لینک:</b> {bio_preview}\n\n"
        "👇 برای تغییر هر مورد روی دکمه مربوطه بزن:"
    )


def stats_text(received: int, sent: int, blocked: int) -> str:
    return (
        "📊 <b>آمار فعالیت تو</b>\n\n"
        f"📥 <b>پیام‌های دریافتی:</b> <code>{received}</code>\n"
        f"📤 <b>پیام‌های ارسالی:</b> <code>{sent}</code>\n"
        f"🚫 <b>کاربران مسدود شده:</b> <code>{blocked}</code>"
    )


def help_text() -> str:
    return (
        "❓ <b>راهنمای استفاده از ربات</b>\n\n"
        "1️⃣ از بخش <b>🔗 لینک ناشناس من</b> لینک اختصاصی خودت رو بگیر.\n"
        "2️⃣ لینک رو توی بیو تلگرام، اینستاگرام یا استوری قرار بده.\n"
        "3️⃣ هرکس روی لینکت بزنه می‌تونه برات پیام ناشناس (متن، عکس، ویس و...) بفرسته.\n"
        "4️⃣ زیر هر پیام دکمه <b>💬 پاسخ</b> هست تا راحت جواب بدی، یا با <b>🚫 مسدود کردن</b> "
        "جلوی افراد مزاحم رو بگیری.\n\n"
        "🔒 <i>حریم خصوصی: هیچ نام کاربری یا آیدی از فرستنده نمایش داده نمی‌شه.</i>"
    )
