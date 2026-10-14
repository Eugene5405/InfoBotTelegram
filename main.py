import os
import asyncio
import threading
from flask import Flask

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

from bot.languages.messages import ALL_LANGUAGES, LANG_BUTTONS
from bot.utils.language import (
    get_user_lang, set_user_lang, set_user_location, get_user_location
)
from bot.dst.handler import time_handler, dst_handler
from bot.weather.handler import (
    current_handler, week_handler, hourly_handler, tomorrow_handler,
    rain_handler, air_handler, uv_handler, sun_handler, wind_handler, alerts_handler
)
from bot.weather.service import get_timezone

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Info Bot is running ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

def lang_kb():
    rows = []
    for i in range(0, len(LANG_BUTTONS), 2):
        row = [KeyboardButton(LANG_BUTTONS[i][0])]
        if i + 1 < len(LANG_BUTTONS):
            row.append(KeyboardButton(LANG_BUTTONS[i + 1][0]))
        rows.append(row)
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def main_kb(lang: str):
    t = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])["buttons"]
    return ReplyKeyboardMarkup([
        [KeyboardButton(t["change_location"]), KeyboardButton(t["help"]), KeyboardButton(t["show_time"])],
        [KeyboardButton(t["share_location"], request_location=True), KeyboardButton(t["weather_commands"])],
    ], resize_keyboard=True)

def weather_kb(lang: str):
    t = ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"])["buttons"]
    return ReplyKeyboardMarkup([
        [KeyboardButton(t["current"]), KeyboardButton(t["week"])],
        [KeyboardButton(t["hourly"]), KeyboardButton(t["tomorrow"])],
        [KeyboardButton(t["rain"]), KeyboardButton(t["air"])],
        [KeyboardButton(t["uv"]), KeyboardButton(t["sun"])],
        [KeyboardButton(t["wind"]), KeyboardButton(t["alerts"])],
        [KeyboardButton(t["back"])],
    ], resize_keyboard=True)

def get_texts(user_id: int):
    lang = get_user_lang(user_id)
    return ALL_LANGUAGES.get(lang, ALL_LANGUAGES["en"]), lang

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texts, _ = get_texts(update.effective_user.id)
    await update.message.reply_text(texts["choose_lang"], reply_markup=lang_kb())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texts, lang = get_texts(update.effective_user.id)
    await update.message.reply_text(texts["help"], reply_markup=main_kb(lang))

async def change_location_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texts, lang = get_texts(update.effective_user.id)
    kb = ReplyKeyboardMarkup([
        [KeyboardButton(texts["buttons"]["share_location"], request_location=True)],
        [KeyboardButton(texts["buttons"]["back"])],
    ], resize_keyboard=True)
    await update.message.reply_text(texts["share_prompt"], reply_markup=kb)

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    user_id = update.effective_user.id
    lat, lon = loc.latitude, loc.longitude
    tz = get_timezone(lat, lon)
    set_user_location(user_id, lat, lon, tz=tz)
    texts, lang = get_texts(user_id)
    await update.message.reply_text(texts["location_saved"], reply_markup=main_kb(lang))

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    txt = update.message.text.strip()
    user_id = update.effective_user.id

    for label, code in LANG_BUTTONS:
        if txt == label:
            set_user_lang(user_id, code)
            texts = ALL_LANGUAGES[code]
            await update.message.reply_text(texts["lang_set"], reply_markup=main_kb(code))
            await update.message.reply_text(texts["welcome"], reply_markup=main_kb(code))
            return

    texts, lang = get_texts(user_id)
    btns = texts["buttons"]

    if txt == btns["help"]:
        await help_cmd(update, context)
        return
    if txt == btns["show_time"]:
        await time_handler(update, context)
        return
    if txt == btns["change_location"]:
        await change_location_prompt(update, context)
        return
    if txt == btns["weather_commands"]:
        await update.message.reply_text(texts["weather_menu"], reply_markup=weather_kb(lang))
        return
    if txt == btns["back"]:
        await update.message.reply_text(texts["main_menu"], reply_markup=main_kb(lang))
        return
    if txt == btns["current"]:
        await current_handler(update, context)
        return
    if txt == btns["week"]:
        await week_handler(update, context)
        return
    if txt == btns["hourly"]:
        await hourly_handler(update, context)
        return
    if txt == btns["tomorrow"]:
        await tomorrow_handler(update, context)
        return
    if txt == btns["rain"]:
        await rain_handler(update, context)
        return
    if txt == btns["air"]:
        await air_handler(update, context)
        return
    if txt == btns["uv"]:
        await uv_handler(update, context)
        return
    if txt == btns["sun"]:
        await sun_handler(update, context)
        return
    if txt == btns["wind"]:
        await wind_handler(update, context)
        return
    if txt == btns["alerts"]:
        await alerts_handler(update, context)
        return

async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await time_handler(update, context)

async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await current_handler(update, context)

async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await week_handler(update, context)

async def cmd_hourly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await hourly_handler(update, context)

async def cmd_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tomorrow_handler(update, context)

async def cmd_rain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rain_handler(update, context)

async def cmd_air(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await air_handler(update, context)

async def cmd_uv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await uv_handler(update, context)

async def cmd_sun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await sun_handler(update, context)

async def cmd_wind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await wind_handler(update, context)

async def cmd_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await alerts_handler(update, context)

async def cmd_change_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await change_location_prompt(update, context)

def main():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    threading.Thread(target=run_flask, daemon=True).start()

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден!")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("time", cmd_watch))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("current", cmd_weather))
    app.add_handler(CommandHandler("week", cmd_week))
    app.add_handler(CommandHandler("hourly", cmd_hourly))
    app.add_handler(CommandHandler("tomorrow", cmd_tomorrow))
    app.add_handler(CommandHandler("rain", cmd_rain))
    app.add_handler(CommandHandler("air", cmd_air))
    app.add_handler(CommandHandler("uv", cmd_uv))
    app.add_handler(CommandHandler("sun", cmd_sun))
    app.add_handler(CommandHandler("wind", cmd_wind))
    app.add_handler(CommandHandler("alerts", cmd_alerts))
    app.add_handler(CommandHandler("change_location", cmd_change_location))
    app.add_handler(CommandHandler("dst", dst_handler))

    app.add_handler(MessageHandler(filters.LOCATION, location_received))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))

    print("✅ Info Bot started")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
