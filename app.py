from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load API key from .env
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = request.form['city']
        weather_data = get_weather(city)
        return render_template('index.html', weather=weather_data)
    return render_template('index.html', weather=None)

def get_weather(city):
    API_KEY = os.getenv('OPENWEATHER_API_KEY')  # Or paste key directly
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # Celsius
        'cnt': 40  # 5 days (8 forecasts/day)
    }
    response = requests.get(base_url, params=params).json()
    
    # Extract daily forecasts (8 entries/day → 1/day)
    forecasts = []
    for entry in response['list'][::8]:  # Take every 8th entry (24h apart)
        forecasts.append({
            'date': entry['dt_txt'],
            'temp': entry['main']['temp'],
            'description': entry['weather'][0]['description'],
            'icon': entry['weather'][0]['icon']
        })
    return {
        'city': city,
        'current': forecasts[0],  # Today
        'forecast': forecasts[1:]  # Next 7 days
    }

if __name__ == '__main__':
    app.run(debug=True)