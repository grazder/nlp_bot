import requests

OPEN_WEATHER_TOKEN = "OPEN_WEATHER_TOKEN"

if __name__ == '__main__':
    city_name = 'Глазов'
    current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}' \
                              f'&units=metric&appid={OPEN_WEATHER_TOKEN}'
    current_weather = requests.get(current_weather_request).json()

    lon, lat = current_weather['coord']['lon'], current_weather['coord']['lat']
    temperature = current_weather['main']['temp']
    weather = current_weather['weather'][0]['main']

    weather_forecast_request = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}' \
                               f'&exclude=minutely,hourly&units=metric&appid={OPEN_WEATHER_TOKEN}'
    weather_forecast = requests.get(weather_forecast_request).json()

    forecasts = []
    for forecast in weather_forecast['daily']:
        day_temp = forecast['temp']['day']
        night_temp = forecast['temp']['night']
        weather = forecast['weather'][0]['main']

        forecasts.append((day_temp, night_temp, weather))
        print(f'Температура днем: {day_temp}, ночью: {night_temp}, {weather}')
