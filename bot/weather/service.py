import requests
from datetime import datetime

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

WMO_EMOJI = {
    0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️",
    45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦", 81: "🌧", 82: "🌧",
    95: "⛈", 96: "⛈", 99: "⛈",
}

def _get_json(url: str, params: dict = None):
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_timezone(lat: float, lon: float) -> str:
    data = _get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon, "timezone": "auto", "current": "temperature_2m",
    })
    return data.get("timezone", "UTC")

def get_current(lat: float, lon: float, lang: str = "en"):
    data = _get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
        "timezone": "auto",
    })
    if "error" in data or "current" not in data:
        return None
    cur = data["current"]
    code = cur.get("weather_code", 0)
    return {
        "temp": cur.get("temperature_2m"),
        "feels": cur.get("apparent_temperature"),
        "humidity": cur.get("relative_humidity_2m"),
        "wind": cur.get("wind_speed_10m"),
        "wind_dir": cur.get("wind_direction_10m"),
        "code": code,
        "desc": WMO_CODES.get(code, "Unknown"),
        "emoji": WMO_EMOJI.get(code, "🌤"),
        "tz": data.get("timezone", "UTC"),
    }

def get_daily(lat: float, lon: float, days: int = 7):
    data = _get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum",
        "timezone": "auto", "forecast_days": days,
    })
    if "error" in data or "daily" not in data:
        return None
    return data

def get_hourly(lat: float, lon: float, hours: int = 24):
    data = _get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,weather_code,precipitation_probability",
        "timezone": "auto", "forecast_hours": hours,
    })
    if "error" in data or "hourly" not in data:
        return None
    return data

def get_air(lat: float, lon: float):
    data = _get_json("https://air-quality-api.open-meteo.com/v1/air-quality", {
        "latitude": lat, "longitude": lon,
        "current": "european_aqi,pm2_5,pm10", "timezone": "auto",
    })
    if "error" in data or "current" not in data:
        return None
    return data["current"]

def get_uv_and_sun(lat: float, lon: float):
    data = _get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "daily": "uv_index_max,sunrise,sunset", "timezone": "auto", "forecast_days": 1,
    })
    if "error" in data or "daily" not in data:
        return None
    d = data["daily"]
    return {
        "uv": d["uv_index_max"][0] if d.get("uv_index_max") else None,
        "sunrise": d["sunrise"][0] if d.get("sunrise") else None,
        "sunset": d["sunset"][0] if d.get("sunset") else None,
        "tz": data.get("timezone", "UTC"),
    }

def get_wind(lat: float, lon: float):
    data = _get_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "daily": "wind_speed_10m_max,wind_direction_10m_dominant",
        "timezone": "auto", "forecast_days": 1,
    })
    if "error" in data:
        return None
    return data

def wind_dir_name(deg: float) -> str:
    if deg is None:
        return "?"
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((deg + 11.25) / 22.5) % 16
    return dirs[ix]

def aqi_label(aqi: float) -> str:
    if aqi is None: return "Unknown"
    if aqi <= 20: return "Good"
    if aqi <= 40: return "Fair"
    if aqi <= 60: return "Moderate"
    if aqi <= 80: return "Poor"
    if aqi <= 100: return "Very Poor"
    return "Extremely Poor"

def uv_label(uv: float) -> str:
    if uv is None: return "Unknown"
    if uv < 3: return "Low"
    if uv < 6: return "Moderate"
    if uv < 8: return "High"
    if uv < 11: return "Very High"
    return "Extreme"
