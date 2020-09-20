import json
import os
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Callable

import requests
from flask import render_template, Flask
from flask import request

API_KEY = os.environ["API_KEY"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API = BASE_URL + "?q={city_name}&appid={api_key}&units=metric"

app = Flask(__name__)


@dataclass
class WeatherInfo:
    """Stores weather information."""

    temp: float
    sunset: str
    sunrise: str
    temp_min: float
    temp_max: float
    desc: str

    @classmethod
    def from_dict(cls, data: dict) -> "WeatherInfo":
        return cls(
            temp=data["main"]["temp"],
            temp_min=data["main"]["temp_min"],
            temp_max=data["main"]["temp_max"],
            desc=data["weather"][0]["main"],
            sunset=format_date(data["sys"]["sunset"]),
            sunrise=format_date(data["sys"]["sunrise"]),
        )


@app.route("/")
@app.route("/index")
def index():
    """Given a city name passed as query parameter. Display a weather summary."""
    city = request.args.get("city")
    weather_info = retrieve_weather_with_adapter(city, adapter=requests_adapter)
    return render_template("index.html", city=city, weather_info=asdict(weather_info))


def find_weather_for(city: str) -> dict:
    """Queries the weather API and returns the weather data for a particular city."""
    url = API.format(city_name=city, api_key=API_KEY)
    resp = requests.get(url)
    return resp.json()


def requests_adapter(url: str) -> dict:
    """An adapter that encapsulates requests.get"""
    resp = requests.get(url)
    return resp.json()


def urllib_adapter(url: str) -> dict:
    """An adapter that encapsulates urllib.urlopen"""
    with urllib.request.urlopen(url) as response:
        resp = response.read()
    return json.loads(resp)


def find_weather_with_adapter_for(city: str, adapter: Callable[[str], dict]) -> dict:
    """Find the weather using an adapter."""
    url = API.format(city_name=city, api_key=API_KEY)
    return adapter(url)


def retrieve_weather_with_adapter(
    city: str, adapter: Callable[[str], dict] = requests_adapter
) -> WeatherInfo:
    """Retrieve weather implementation that uses an adapter."""
    data = find_weather_with_adapter_for(city, adapter=adapter)
    return WeatherInfo.from_dict(data)


def retrieve_weather(city: str) -> WeatherInfo:
    """Finds the weather for a city and returns a WeatherInfo instance."""
    data = find_weather_for(city)
    return WeatherInfo.from_dict(data)


def format_date(timestamp: int) -> str:
    """Formats a timestamp into date time."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%m/%d/%Y, %H:%M:%S")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
