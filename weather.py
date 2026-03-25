import json
import os

import requests
from dotenv import load_dotenv

_ = load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(location, time="now"):
    """Get real current weather from OpenWeatherMap."""
    if not OPENWEATHER_API_KEY:
        return json.dumps({"error": "OPENWEATHER_API_KEY is missing in .env"})

    try:
        geo_resp = requests.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params={"q": location, "limit": 1, "appid": OPENWEATHER_API_KEY},
            timeout=10,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if not geo_data:
            return json.dumps({"error": f"Could not find location: {location}"})

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        resolved_name = geo_data[0].get("name", location)
        country = geo_data[0].get("country", "")

        weather_resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=10,
        )
        weather_resp.raise_for_status()
        w = weather_resp.json()

        return json.dumps(
            {
                "location": f"{resolved_name}, {country}".strip(", "),
                "temperature_c": w["main"]["temp"],
                "feels_like_c": w["main"]["feels_like"],
                "condition": w["weather"][0]["description"],
                "humidity": w["main"]["humidity"],
                "time": time,
            }
        )
    except Exception as e:
        return json.dumps({"error": f"Weather API failed: {str(e)}"})
