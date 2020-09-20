import json
from http import HTTPStatus

import pytest
import responses
import vcr

from weather_app import (
    app,
    API,
    API_KEY,
    retrieve_weather_with_adapter,
    WeatherInfo,
    retrieve_weather,
    urllib_adapter,
)


@pytest.fixture()
def fake_weather_info():
    """Fixture that returns a static weather data."""
    with open("tests/resources/weather.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def client():
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


def test_retrieve_weather_using_mocks(mocker, fake_weather_info):
    """Given a city name, test that a HTML report about the weather is generated
    correctly."""
    # Creates a fake requests response object
    fake_resp = mocker.Mock()
    # Mock the json method to return the static weather data
    fake_resp.json = mocker.Mock(return_value=fake_weather_info)
    # Mock the status code
    fake_resp.status_code = HTTPStatus.OK

    mocker.patch("weather_app.requests.get", return_value=fake_resp)

    weather_info = retrieve_weather(city="London")
    assert weather_info == WeatherInfo.from_dict(fake_weather_info)


@responses.activate
def test_retrieve_weather_using_responses(fake_weather_info):
    """Given a city name, test that a HTML report about the weather is generated
    correctly."""
    api_uri = API.format(city_name="London", api_key=API_KEY)
    responses.add(responses.GET, api_uri, json=fake_weather_info, status=HTTPStatus.OK)

    weather_info = retrieve_weather(city="London")
    assert weather_info == WeatherInfo.from_dict(fake_weather_info)


@responses.activate
def test_retrieve_weather_using_adapter(
    fake_weather_info,
):
    def fake_adapter(url: str):
        return fake_weather_info

    weather_info = retrieve_weather_with_adapter(city="London", adapter=fake_adapter)
    assert weather_info == WeatherInfo.from_dict(fake_weather_info)


@vcr.use_cassette()
def test_retrieve_weather_using_vcr(fake_weather_info):
    weather_info = retrieve_weather(city="London")
    assert weather_info == WeatherInfo.from_dict(fake_weather_info)


@vcr.use_cassette("tests/test_retrieve_weather_using_vcr")
def test_retrieve_weather_using_vcr_and_adapter(fake_weather_info):
    weather_info = retrieve_weather_with_adapter(city="London", adapter=urllib_adapter)
    assert weather_info == WeatherInfo.from_dict(fake_weather_info)


@responses.activate
def test_weather_app_using_responses(client, fake_weather_info):
    api_uri = API.format(city_name="London", api_key=API_KEY)
    responses.add(responses.GET, api_uri, json=fake_weather_info, status=HTTPStatus.OK)

    resp = client.get("/?city=London")
    assert resp.status_code == HTTPStatus.OK
    assert b"City: London!" in resp.data
    assert b"Clear" in resp.data
    assert b"16.53 \xc2\xbaC" in resp.data
    assert b"Sunrise: 09/18/2020, 06:40:46" in resp.data
    assert b"Sunset: 09/18/2020, 19:08:29" in resp.data


def test_weather_app_using_mocks(client, mocker, fake_weather_info):
    """Given a city name, test that a HTML report about the weather is generated
    correctly."""
    mocker.patch("weather_app.find_weather_for", return_value=fake_weather_info)
    resp = client.get("/?city=London")
    assert resp.status_code == HTTPStatus.OK
    assert b"City: London!" in resp.data
    assert b"Clear" in resp.data
    assert b"16.53 \xc2\xbaC" in resp.data
    assert b"Sunrise: 09/18/2020, 06:40:46" in resp.data
    assert b"Sunset: 09/18/2020, 19:08:29" in resp.data


@vcr.use_cassette()
def test_weather_app_using_mocks(client, fake_weather_info):
    """Given a city name, test that a HTML report about the weather is generated
    correctly."""
    resp = client.get("/?city=London")
    assert resp.status_code == HTTPStatus.OK
    assert b"City: London!" in resp.data
    assert b"Clear" in resp.data
    assert b"16.53 \xc2\xbaC" in resp.data
    assert b"Sunrise: 09/18/2020, 06:40:46" in resp.data
    assert b"Sunset: 09/18/2020, 19:08:29" in resp.data
