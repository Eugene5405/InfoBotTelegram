from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import pytz

from bot.utils.language import get_user_location

async def time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lat, lon, tz_name, city = get_user_location(user_id)
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Europe/Belgrade")
    now = datetime.now(tz)
    time_str = now.strftime("%A, %d %B %Y at %H:%M:%S %Z")
    text = f"⏰ Current time in {tz_name}:\n{time_str}"
    await update.message.reply_text(text)

async def dst_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lat, lon, tz_name, city = get_user_location(user_id)
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        offset = now.strftime("%z")
        is_dst = bool(now.dst())
        status = "DST is active (summer time)" if is_dst else "Standard time (winter)"
        text = (
            f"⏰ Timezone info for {tz_name}:\n"
            f"Current offset: UTC{offset[:3]}:{offset[3:]}\n"
            f"{status}"
        )
    except Exception:
        text = "⚠️ Could not determine DST status."
    await update.message.reply_text(text)
