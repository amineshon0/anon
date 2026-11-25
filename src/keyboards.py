from urllib.parse import quote
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# متن دکمه‌های کیبورد پایین صفحه
BTN_MY_LINK = "🔗 لینک ناشناس من"
BTN_SETTINGS = "⚙️ تنظیمات"
BTN_STATS = "📊 آمار من"
BTN_HELP = "❓ راهنما"
BTN_ADMIN = "🛡️ پنل مدیریت"


def home_reply_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """کیبورد دائمی پایین صفحه تا نیازی به تایپ هیچ دستوری نباشد."""
    rows = [
        [KeyboardButton(BTN_MY_LINK)],
        [KeyboardButton(BTN_SETTINGS), KeyboardButton(BTN_STATS)],
        [KeyboardButton(BTN_HELP)],
    ]
    if is_admin:
        rows.append([KeyboardButton(BTN_ADMIN)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(BTN_MY_LINK, callback_data="menu:link")],
        [
            InlineKeyboardButton(BTN_SETTINGS, callback_data="menu:settings"),
            InlineKeyboardButton(BTN_STATS, callback_data="menu:stats"),
        ],
        [InlineKeyboardButton(BTN_HELP, callback_data="menu:help")],
    ]
    if is_admin:
        rows.append([InlineKeyboardButton(BTN_ADMIN, callback_data="menu:admin")])
    return InlineKeyboardMarkup(rows)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="menu:admin")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="menu:home")],
        ]
    )


def link_keyboard(link: str) -> InlineKeyboardMarkup:
    share_text = quote("برام یه پیام ناشناس بفرست! 👇✨")
    share_url = f"https://t.me/share/url?url={quote(link)}&text={share_text}"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📤 اشتراک‌گذاری لینک", url=share_url)],
            [InlineKeyboardButton("🔄 ساخت لینک جدید", callback_data="link:regen")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="menu:home")],
        ]
    )


def settings_keyboard(is_accepting: bool) -> InlineKeyboardMarkup:
    toggle_label = (
        "🔴 غیرفعال کردن دریافت پیام" if is_accepting else "🟢 فعال کردن دریافت پیام"
    )
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(toggle_label, callback_data="settings:toggle")],
            [
                InlineKeyboardButton(
                    "📝 تنظیم متن خوش‌آمدگویی", callback_data="settings:bio"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔓 رفع مسدودیت همه کاربران", callback_data="settings:unblock_all"
                )
            ],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="menu:home")],
        ]
    )


def back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 منوی اصلی", callback_data="menu:home")]]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ انصراف", callback_data="action:cancel")]]
    )


def incoming_message_keyboard(msg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💬 پاسخ به این پیام", callback_data=f"msg:reply:{msg_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🚫 مسدود کردن فرستنده", callback_data=f"msg:block:{msg_id}"
                )
            ],
        ]
    )


def after_send_keyboard(target_code: str | None = None) -> InlineKeyboardMarkup:
    rows = []
    if target_code:
        rows.append(
            [
                InlineKeyboardButton(
                    "✉️ ارسال پیام دیگر", callback_data=f"send:again:{target_code}"
                )
            ]
        )
    rows.append([InlineKeyboardButton("🏠 منوی اصلی", callback_data="menu:home")])
    return InlineKeyboardMarkup(rows)
