from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', weather=None)

@app.route('/get_weather', methods=['POST'])
def get_weather():
    start_time = time.time()
    
    city = request.form['city']
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    # Step 1: Get precise coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url).json()
    
    if not geo_response:
        return jsonify({"error": "City not found"}), 404
        
    lat, lon = geo_response[0]['lat'], geo_response[0]['lon']
    
    # Step 2: Get weather data with precise coordinates
    weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    weather_data = requests.get(weather_url).json()
    
    # Process current weather
    current = weather_data['list'][0]
    
    # Process 5-day forecast (one entry per day at 12:00 PM local time)
    forecast = []
    today = datetime.now().date()
    for day_offset in range(1, 6):
        target_date = today + timedelta(days=day_offset)
        target_time = datetime.combine(target_date, datetime.strptime("12:00:00", "%H:%M:%S").time())
        
        # Find the closest forecast to 12:00 PM
        closest_forecast = None
        min_diff = float('inf')
        
        for entry in weather_data['list']:
            entry_time = datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
            time_diff = abs((target_time - entry_time).total_seconds())
            
            if time_diff < min_diff:
                min_diff = time_diff
                closest_forecast = entry
        
        if closest_forecast:
            forecast.append({
                "date": closest_forecast['dt_txt'],
                "temp": closest_forecast['main']['temp'],
                "icon": closest_forecast['weather'][0]['icon'],
                "description": closest_forecast['weather'][0]['description']
            })
    
    processing_time = round((time.time() - start_time) * 1000, 2)
    
    return jsonify({
        "city": city,
        "coords": {"lat": lat, "lon": lon},
        "current": {
            "temp": current['main']['temp'],
            "humidity": current['main']['humidity'],
            "wind": current['wind']['speed'],
            "description": current['weather'][0]['description'],
            "icon": current['weather'][0]['icon'],
            "time": current['dt_txt']
        },
        "forecast": forecast,
        "response_time": processing_time
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
