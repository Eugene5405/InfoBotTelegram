from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from bot.utils.language import get_user_lang, get_user_location
from bot.languages.messages import ALL_LANGUAGES
from bot.weather.service import (
    get_current, get_daily, get_hourly, get_air, get_uv_and_sun, get_wind,
    wind_dir_name, aqi_label, uv_label, WMO_CODES, WMO_EMOJI
)

def _loc(user_id):
    return get_user_location(user_id)

def _msg(update: Update):
    return update.message or (update.callback_query.message if update.callback_query else None)

async def current_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        texts = ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])
        await msg.reply_text(texts["no_location"])
        return
    data = get_current(lat, lon)
    if not data:
        await msg.reply_text("⚠️ Could not fetch weather. Try again later.")
        return
    text = (
        f"🌤 Weather at your saved location:\n"
        f"Timezone: {data['tz']}\n"
        f"{data['emoji']} {data['desc']}\n"
        f"Temperature: {data['temp']:.1f} °C\n"
        f"Feels like: {data['feels']:.1f} °C\n"
        f"Humidity: {data['humidity']}%\n"
        f"Wind: {data['wind']:.1f} km/h"
    )
    await msg.reply_text(text)

async def week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_daily(lat, lon, 7)
    if not data:
        await msg.reply_text("⚠️ Could not fetch forecast.")
        return
    daily = data["daily"]
    lines = [f"📅 7-day weather at your saved location:\nTimezone: {data.get('timezone', tz)}\n"]
    for i in range(len(daily["time"])):
        date = daily["time"][i]
        code = daily["weather_code"][i]
        tmin = daily["temperature_2m_min"][i]
        tmax = daily["temperature_2m_max"][i]
        rain = daily["precipitation_probability_max"][i]
        emoji = WMO_EMOJI.get(code, "🌤")
        desc = WMO_CODES.get(code, "")
        try:
            d = datetime.fromisoformat(date)
            day_name = d.strftime("%a %d %b")
        except:
            day_name = date
        lines.append(f"{day_name}: {emoji} {desc}, {tmin:.1f}°C to {tmax:.1f}°C, rain {rain}%")
    await msg.reply_text("\n".join(lines))

async def hourly_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_hourly(lat, lon, 24)
    if not data:
        await msg.reply_text("⚠️ Could not fetch hourly forecast.")
        return
    hourly = data["hourly"]
    lines = ["🕐 Hourly forecast (next 24h):\n"]
    for i in range(min(24, len(hourly["time"]))):
        t = hourly["time"][i]
        temp = hourly["temperature_2m"][i]
        code = hourly["weather_code"][i]
        rain = hourly["precipitation_probability"][i]
        emoji = WMO_EMOJI.get(code, "🌤")
        desc = WMO_CODES.get(code, "")
        try:
            dt = datetime.fromisoformat(t)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = t
        lines.append(f"{time_str}: {emoji} {desc}, {temp:.1f}°C, rain {rain}%")
    text = "\n".join(lines)
    if len(text) > 4000:
        await msg.reply_text("\n".join(lines[:13]))
        await msg.reply_text("\n".join(lines[13:]))
    else:
        await msg.reply_text(text)

async def tomorrow_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_daily(lat, lon, 2)
    if not data or len(data["daily"]["time"]) < 2:
        await msg.reply_text("⚠️ Could not fetch tomorrow forecast.")
        return
    daily = data["daily"]
    i = 1
    code = daily["weather_code"][i]
    tmin = daily["temperature_2m_min"][i]
    tmax = daily["temperature_2m_max"][i]
    rain = daily["precipitation_probability_max"][i]
    precip = daily["precipitation_sum"][i]
    emoji = WMO_EMOJI.get(code, "🌤")
    desc = WMO_CODES.get(code, "")
    text = (
        f"🌤 Tomorrow at your saved location:\n"
        f"{daily['time'][i]}\n"
        f"{emoji} {desc}\n"
        f"Temperature: {tmin:.1f} to {tmax:.1f} °C\n"
        f"Rain chance: {rain}%\n"
        f"Expected precipitation: {precip:.1f} mm"
    )
    await msg.reply_text(text)

async def rain_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_daily(lat, lon, 1)
    if not data:
        await msg.reply_text("⚠️ Could not fetch rain forecast.")
        return
    daily = data["daily"]
    rain = daily["precipitation_probability_max"][0]
    precip = daily["precipitation_sum"][0]
    date = daily["time"][0]
    if rain >= 50:
        status = "Rain is possible today."
    elif rain >= 20:
        status = "Light rain possible."
    else:
        status = "Rain is unlikely today."
    text = (
        f"🌧 Rain forecast for {date}:\n"
        f"{status}\n"
        f"Maximum chance: {rain}%\n"
        f"Expected precipitation: {precip:.1f} mm"
    )
    await msg.reply_text(text)

async def air_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_air(lat, lon)
    if not data:
        await msg.reply_text("⚠️ Could not fetch air quality.")
        return
    aqi = data.get("european_aqi")
    pm25 = data.get("pm2_5")
    pm10 = data.get("pm10")
    text = (
        f"💨 Air quality at your saved location:\n"
        f"European AQI: {aqi:.0f} ({aqi_label(aqi)})\n"
        f"PM2.5: {pm25:.1f} μg/m³\n"
        f"PM10: {pm10:.1f} μg/m³"
    )
    await msg.reply_text(text)

async def uv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_uv_and_sun(lat, lon)
    if not data or data.get("uv") is None:
        await msg.reply_text("⚠️ Could not fetch UV index.")
        return
    uv = data["uv"]
    advice = "Normal sun protection is recommended." if uv < 6 else "High protection recommended (SPF 30+)."
    text = (
        f"☀️ UV index for today:\n"
        f"Maximum UV index: {uv:.1f} ({uv_label(uv)})\n"
        f"{advice}"
    )
    await msg.reply_text(text)

async def sun_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_uv_and_sun(lat, lon)
    if not data:
        await msg.reply_text("⚠️ Could not fetch sun times.")
        return
    sunrise = data.get("sunrise", "?")
    sunset = data.get("sunset", "?")
    try:
        sunrise = sunrise.split("T")[1][:5]
        sunset = sunset.split("T")[1][:5]
    except:
        pass
    text = (
        f"🌅 Sun times at your saved location:\n"
        f"Sunrise: {sunrise}\n"
        f"Sunset: {sunset}\n"
        f"Timezone: {data.get('tz', tz)}"
    )
    await msg.reply_text(text)

async def wind_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_wind(lat, lon)
    if not data:
        await msg.reply_text("⚠️ Could not fetch wind data.")
        return
    cur = data.get("current", {})
    daily = data.get("daily", {})
    speed = cur.get("wind_speed_10m")
    direction = cur.get("wind_direction_10m")
    max_speed = daily.get("wind_speed_10m_max", [None])[0]
    dom_dir = daily.get("wind_direction_10m_dominant", [None])[0]
    text = (
        f"💨 Wind at your saved location:\n"
        f"Now: {speed:.1f} km/h {wind_dir_name(direction)}\n"
        f"Today's maximum: {max_speed:.1f} km/h\n"
        f"Dominant direction: {wind_dir_name(dom_dir)}"
    )
    await msg.reply_text(text)

async def alerts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = _msg(update)
    user_id = update.effective_user.id
    lat, lon, tz, city = _loc(user_id)
    if lat is None:
        await msg.reply_text(ALL_LANGUAGES.get(get_user_lang(user_id), ALL_LANGUAGES["en"])["no_location"])
        return
    data = get_daily(lat, lon, 1)
    if not data:
        await msg.reply_text("⚠️ Could not check alerts.")
        return
    rain = data["daily"]["precipitation_probability_max"][0]
    if rain >= 70:
        text = f"⚠️ Weather alerts for today:\nHeavy rain is possible ({rain}% chance)."
    elif rain >= 40:
        text = f"⚠️ Weather alerts for today:\nRain is possible ({rain}% chance)."
    else:
        text = "✅ Weather alerts for today:\nNo significant warnings."
    await msg.reply_text(text)
