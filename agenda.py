import requests

def get_weather_forecast():
    """
    Fetches the weather forecast for Rebstein for the rest of the week.
    """
    api_key = "your_api_key_here"  # Replace with your actual API key
    location = "Rebstein,CH"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching weather data.")
        return None

def generate_agenda(weather_data):
    """
    Generates an agenda of things to do in Rebstein for the rest of the week based on the weather forecast.
    """
    agenda = []
    if not weather_data:
        return agenda

    for forecast in weather_data['list']:
        date = forecast['dt_txt']
        weather = forecast['weather'][0]['description']
        temp = forecast['main']['temp']

        if "rain" in weather or "snow" in weather:
            activity = "Visit a museum or enjoy indoor activities"
        elif temp > 25:
            activity = "Go swimming or have a picnic in the park"
        else:
            activity = "Take a hike or explore the town"

        agenda.append(f"{date}: {activity} (Weather: {weather}, Temp: {temp}°C)")

    return agenda

def main():
    weather_data = get_weather_forecast()
    agenda = generate_agenda(weather_data)
    if agenda:
        print("Agenda for the rest of the week in Rebstein:")
        for item in agenda:
            print(item)
    else:
        print("Could not generate agenda due to lack of weather data.")

if __name__ == "__main__":
    main()


