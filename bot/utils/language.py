USER_DATA = {}

DEFAULT = {
    "lang": "en",
    "lat": 44.7866,
    "lon": 20.4489,
    "tz": "Europe/Belgrade",
    "city": "Belgrade"
}

def get_user(user_id: int) -> dict:
    if user_id not in USER_DATA:
        USER_DATA[user_id] = DEFAULT.copy()
    return USER_DATA[user_id]

def get_user_lang(user_id: int) -> str:
    return get_user(user_id).get("lang", "en")

def set_user_lang(user_id: int, lang: str):
    data = get_user(user_id)
    data["lang"] = lang

def set_user_location(user_id: int, lat: float, lon: float, tz: str = None, city: str = None):
    data = get_user(user_id)
    data["lat"] = lat
    data["lon"] = lon
    if tz:
        data["tz"] = tz
    if city:
        data["city"] = city

def get_user_location(user_id: int):
    data = get_user(user_id)
    return data.get("lat"), data.get("lon"), data.get("tz", "Europe/Belgrade"), data.get("city", "Unknown")
