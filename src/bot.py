import logging
import os
import threading
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config import ADMIN_IDS, BOT_TOKEN, DATABASE_PATH
from src.database import Database
from src.keyboards import (
    BTN_ADMIN,
    BTN_HELP,
    BTN_MY_LINK,
    BTN_SETTINGS,
    BTN_STATS,
    admin_panel_keyboard,
    after_send_keyboard,
    back_home_keyboard,
    cancel_keyboard,
    home_reply_keyboard,
    incoming_message_keyboard,
    link_keyboard,
    main_menu_keyboard,
    settings_keyboard,
)
from src.texts import (
    help_text,
    incoming_message_header,
    incoming_text_card,
    message_sent_text,
    my_link_text,
    reply_prompt_text,
    send_prompt_text,
    settings_text,
    stats_text,
    welcome_home,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

db = Database(DATABASE_PATH)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK - Anonymous Telegram Bot is running")

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return


def _start_health_server() -> None:
    """Starts a tiny HTTP server when PORT is set (for free cloud hosts like Render/Koyeb)."""
    port_raw = os.getenv("PORT", "").strip()
    if not port_raw.isdigit():
        return
    port = int(port_raw)
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Healthcheck HTTP server listening on port %s", port)


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _clear_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("mode", None)
    context.user_data.pop("target_id", None)
    context.user_data.pop("target_code", None)
    context.user_data.pop("reply_to_msg_id", None)


async def _build_user_link(context: ContextTypes.DEFAULT_TYPE, link_code: str) -> str:
    bot_username = context.bot.username
    return f"https://t.me/{bot_username}?start=u_{link_code}"


def _admin_stats_text() -> str:
    stats = db.get_global_stats()
    return (
        "🛡️ <b>پنل مدیریت ربات</b>\n\n"
        f"👥 <b>کل کاربران:</b> <code>{stats['users']}</code>\n"
        f"💌 <b>کل پیام‌های ردوبدل شده:</b> <code>{stats['messages']}</code>\n"
        f"👮 <b>تعداد ادمین‌های فعال:</b> <code>{len(ADMIN_IDS)}</code>"
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.effective_message
    if not user or not message:
        return

    _clear_state(context)
    db.get_or_create_user(user.id, user.full_name, user.username)
    is_admin = _is_admin(user.id)

    if context.args and context.args[0].startswith("u_"):
        code = context.args[0][2:]
        await _prompt_anonymous_send(update, context, code)
        return

    await message.reply_text(
        welcome_home(user.first_name),
        parse_mode=ParseMode.HTML,
        reply_markup=home_reply_keyboard(is_admin=is_admin),
    )


async def _prompt_anonymous_send(
    update: Update, context: ContextTypes.DEFAULT_TYPE, code: str
) -> None:
    user = update.effective_user
    target = db.get_user_by_code(code)

    async def respond(text: str, markup=None) -> None:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, parse_mode=ParseMode.HTML, reply_markup=markup
            )
        elif update.effective_message:
            await update.effective_message.reply_text(
                text, parse_mode=ParseMode.HTML, reply_markup=markup
            )

    if not target:
        await respond(
            "⚠️ <b>لینک معتبر نیست یا تغییر کرده است.</b>",
            markup=back_home_keyboard(),
        )
        return

    if user and target["user_id"] == user.id:
        await respond(
            "😄 <b>نمی‌تونی به خودت پیام ناشناس بفرستی!</b>\n\n"
            "لینکت رو برای دوستات بفرست تا برات پیام بذارن.",
            markup=back_home_keyboard(),
        )
        return

    if not target["is_accepting"]:
        await respond(
            "🔕 <b>این کاربر فعلاً دریافت پیام ناشناس را غیرفعال کرده است.</b>",
            markup=back_home_keyboard(),
        )
        return

    if user and db.is_blocked(target["user_id"], user.id):
        await respond(
            "🚫 <b>امکان ارسال پیام به این کاربر وجود ندارد.</b>",
            markup=back_home_keyboard(),
        )
        return

    context.user_data["mode"] = "send"
    context.user_data["target_id"] = target["user_id"]
    context.user_data["target_code"] = target["link_code"]

    await respond(
        send_prompt_text(target["full_name"], target.get("custom_bio", "")),
        markup=cancel_keyboard(),
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if not query or not user:
        return

    await query.answer()
    data = query.data or ""
    db_user = db.get_or_create_user(user.id, user.full_name, user.username)
    is_admin = _is_admin(user.id)

    if data == "menu:home":
        _clear_state(context)
        await query.edit_message_text(
            welcome_home(user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(is_admin=is_admin),
        )
        return

    if data == "menu:link":
        _clear_state(context)
        link = await _build_user_link(context, db_user["link_code"])
        await query.edit_message_text(
            my_link_text(link, bool(db_user["is_accepting"]), db_user["custom_bio"]),
            parse_mode=ParseMode.HTML,
            reply_markup=link_keyboard(link),
        )
        return

    if data == "link:regen":
        new_code = db.regenerate_link_code(user.id)
        link = await _build_user_link(context, new_code)
        await query.edit_message_text(
            "🔄 <b>لینک جدید ساخته شد!</b> (لینک قبلی دیگه کار نمی‌کنه)\n\n"
            + my_link_text(link, bool(db_user["is_accepting"]), db_user["custom_bio"]),
            parse_mode=ParseMode.HTML,
            reply_markup=link_keyboard(link),
        )
        return

    if data == "menu:settings":
        _clear_state(context)
        await query.edit_message_text(
            settings_text(bool(db_user["is_accepting"]), db_user["custom_bio"]),
            parse_mode=ParseMode.HTML,
            reply_markup=settings_keyboard(bool(db_user["is_accepting"])),
        )
        return

    if data == "settings:toggle":
        new_status = db.toggle_accepting(user.id)
        await query.edit_message_text(
            settings_text(new_status, db_user["custom_bio"]),
            parse_mode=ParseMode.HTML,
            reply_markup=settings_keyboard(new_status),
        )
        return

    if data == "settings:bio":
        context.user_data["mode"] = "set_bio"
        await query.edit_message_text(
            "📝 <b>تنظیم متن خوش‌آمدگویی</b>\n\n"
            "متنی که می‌خوای وقتی بقیه روی لینکت کلیک می‌کنن ببینن رو بفرست (حداکثر ۲۰۰ کاراکتر).\n"
            "برای حذف متن، کلمه <code>حذف</code> رو بفرست.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
        return

    if data == "settings:unblock_all":
        count = db.unblock_all(user.id)
        await query.edit_message_text(
            f"🔓 <b>مسدودیت {count} کاربر با موفقیت برداشته شد.</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=back_home_keyboard(),
        )
        return

    if data == "menu:stats":
        _clear_state(context)
        stats = db.get_user_stats(user.id)
        await query.edit_message_text(
            stats_text(stats["received"], stats["sent"], stats["blocked"]),
            parse_mode=ParseMode.HTML,
            reply_markup=back_home_keyboard(),
        )
        return

    if data == "menu:help":
        _clear_state(context)
        await query.edit_message_text(
            help_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=back_home_keyboard(),
        )
        return

    if data == "menu:admin":
        if not is_admin:
            return
        _clear_state(context)
        await query.edit_message_text(
            _admin_stats_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
        return

    if data == "action:cancel":
        _clear_state(context)
        await query.edit_message_text(
            "❌ <b>عملیات لغو شد.</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(is_admin=is_admin),
        )
        return

    if data.startswith("send:again:"):
        code = data.split(":", 2)[2]
        await _prompt_anonymous_send(update, context, code)
        return

    if data.startswith("msg:reply:"):
        msg_id = int(data.split(":")[2])
        record = db.get_message(msg_id)
        if not record or record["receiver_id"] != user.id:
            await query.message.reply_text(
                "⚠️ <b>پیام مورد نظر پیدا نشد.</b>", parse_mode=ParseMode.HTML
            )
            return

        context.user_data["mode"] = "reply"
        context.user_data["target_id"] = record["sender_id"]
        context.user_data["reply_to_msg_id"] = msg_id
        await query.message.reply_text(
            reply_prompt_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
        return

    if data.startswith("msg:block:"):
        msg_id = int(data.split(":")[2])
        record = db.get_message(msg_id)
        if not record or record["receiver_id"] != user.id:
            return

        db.block_user(user.id, record["sender_id"])
        await query.message.reply_text(
            "🚫 <b>فرستنده این پیام مسدود شد.</b>\n"
            "از این به بعد نمی‌تونه برات پیام ناشناس بفرسته.",
            parse_mode=ParseMode.HTML,
        )
        return


async def _deliver_message(
    context: ContextTypes.DEFAULT_TYPE,
    receiver_id: int,
    msg: Message,
    saved_msg_id: int,
    is_reply: bool,
) -> str:
    """Delivers text or media anonymously to the receiver and returns the msg_type."""
    kb = incoming_message_keyboard(saved_msg_id)
    header = incoming_message_header(is_reply=is_reply)
    caption_extra = (
        f"\n\n<blockquote>{escape(msg.caption)}</blockquote>" if msg.caption else ""
    )
    media_caption = f"{header}{caption_extra}"

    if msg.text:
        await context.bot.send_message(
            chat_id=receiver_id,
            text=incoming_text_card(msg.text, is_reply=is_reply),
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        return "text"

    if msg.photo:
        await context.bot.send_photo(
            chat_id=receiver_id,
            photo=msg.photo[-1].file_id,
            caption=media_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        return "photo"

    if msg.voice:
        await context.bot.send_voice(
            chat_id=receiver_id,
            voice=msg.voice.file_id,
            caption=media_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        return "voice"

    if msg.video:
        await context.bot.send_video(
            chat_id=receiver_id,
            video=msg.video.file_id,
            caption=media_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        return "video"

    if msg.audio:
        await context.bot.send_audio(
            chat_id=receiver_id,
            audio=msg.audio.file_id,
            caption=media_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        return "audio"

    if msg.document:
        await context.bot.send_document(
            chat_id=receiver_id,
            document=msg.document.file_id,
            caption=media_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        return "document"

    if msg.sticker:
        await context.bot.send_message(
            chat_id=receiver_id, text=header, parse_mode=ParseMode.HTML
        )
        await context.bot.send_sticker(
            chat_id=receiver_id,
            sticker=msg.sticker.file_id,
            reply_markup=kb,
        )
        return "sticker"

    if msg.video_note:
        await context.bot.send_message(
            chat_id=receiver_id, text=header, parse_mode=ParseMode.HTML
        )
        await context.bot.send_video_note(
            chat_id=receiver_id,
            video_note=msg.video_note.file_id,
            reply_markup=kb,
        )
        return "video_note"

    raise ValueError("unsupported_media")


async def _handle_reply_keyboard_buttons(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
) -> bool:
    """Handles bottom ReplyKeyboard button presses. Returns True if handled."""
    user = update.effective_user
    msg = update.effective_message
    if not user or not msg:
        return False

    db_user = db.get_or_create_user(user.id, user.full_name, user.username)
    is_admin = _is_admin(user.id)

    if text == BTN_MY_LINK:
        _clear_state(context)
        link = await _build_user_link(context, db_user["link_code"])
        await msg.reply_text(
            my_link_text(link, bool(db_user["is_accepting"]), db_user["custom_bio"]),
            parse_mode=ParseMode.HTML,
            reply_markup=link_keyboard(link),
        )
        return True

    if text == BTN_SETTINGS:
        _clear_state(context)
        await msg.reply_text(
            settings_text(bool(db_user["is_accepting"]), db_user["custom_bio"]),
            parse_mode=ParseMode.HTML,
            reply_markup=settings_keyboard(bool(db_user["is_accepting"])),
        )
        return True

    if text == BTN_STATS:
        _clear_state(context)
        stats = db.get_user_stats(user.id)
        await msg.reply_text(
            stats_text(stats["received"], stats["sent"], stats["blocked"]),
            parse_mode=ParseMode.HTML,
            reply_markup=back_home_keyboard(),
        )
        return True

    if text == BTN_HELP:
        _clear_state(context)
        await msg.reply_text(
            help_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=back_home_keyboard(),
        )
        return True

    if text == BTN_ADMIN and is_admin:
        _clear_state(context)
        await msg.reply_text(
            _admin_stats_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
        return True

    return False


async def incoming_user_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = update.effective_user
    msg = update.effective_message
    if not user or not msg:
        return

    db.get_or_create_user(user.id, user.full_name, user.username)
    is_admin = _is_admin(user.id)

    # اگر کاربر یکی از دکمه‌های کیبورد پایین صفحه را زد
    if msg.text and await _handle_reply_keyboard_buttons(update, context, msg.text):
        return

    mode = context.user_data.get("mode")

    if mode == "set_bio":
        if not msg.text:
            await msg.reply_text(
                "⚠️ لطفاً فقط متن ارسال کن.", reply_markup=cancel_keyboard()
            )
            return
        bio = "" if msg.text.strip() == "حذف" else msg.text.strip()
        db.set_custom_bio(user.id, bio)
        _clear_state(context)
        await msg.reply_text(
            "✅ <b>متن خوش‌آمدگویی با موفقیت ذخیره شد!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=home_reply_keyboard(is_admin=is_admin),
        )
        return

    if mode in ("send", "reply"):
        target_id = context.user_data.get("target_id")
        target_code = context.user_data.get("target_code")
        reply_to_msg_id = context.user_data.get("reply_to_msg_id")
        is_reply = mode == "reply"

        if not target_id:
            _clear_state(context)
            return

        if db.is_blocked(target_id, user.id):
            _clear_state(context)
            await msg.reply_text(
                "🚫 <b>امکان ارسال پیام به این کاربر وجود ندارد.</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=back_home_keyboard(),
            )
            return

        saved_msg_id = db.save_message(
            sender_id=user.id,
            receiver_id=target_id,
            msg_type="media" if not msg.text else "text",
            reply_to_msg_id=reply_to_msg_id,
        )

        try:
            await _deliver_message(context, target_id, msg, saved_msg_id, is_reply)
        except ValueError:
            await msg.reply_text(
                "⚠️ این نوع پیام پشتیبانی نمی‌شه. لطفاً متن، عکس، ویس، ویدیو یا استیکر بفرست.",
                reply_markup=cancel_keyboard(),
            )
            return
        except Forbidden:
            _clear_state(context)
            await msg.reply_text(
                "⚠️ <b>متأسفانه این کاربر ربات را مسدود کرده است و پیام به دستش نرسید.</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=back_home_keyboard(),
            )
            return
        except TelegramError as exc:
            logger.exception("Failed to deliver message: %s", exc)
            _clear_state(context)
            await msg.reply_text(
                "⚠️ <b>خطایی در ارسال پیام رخ داد. لطفاً دوباره تلاش کن.</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=back_home_keyboard(),
            )
            return

        _clear_state(context)
        await msg.reply_text(
            message_sent_text(is_reply=is_reply),
            parse_mode=ParseMode.HTML,
            reply_markup=after_send_keyboard(None if is_reply else target_code),
        )
        return

    # پیام پیش‌فرض وقتی کاربر خارج از منو پیام می‌فرستد
    await msg.reply_text(
        "👇 از دکمه‌های زیر استفاده کن:",
        reply_markup=home_reply_keyboard(is_admin=is_admin),
    )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing! Copy .env.example to .env and set your Telegram Bot Token."
        )

    _start_health_server()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, incoming_user_message))

    logger.info("Anonymous Telegram Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
