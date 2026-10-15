# Weather App with Live OpenWeather API

A Python/Tkinter capstone app that fetches real-time temperature, humidity, conditions, wind, pressure, and a 5-day forecast for a searched city/location.

## 1. Requirements
- Python 3.10 or newer
- Internet connection
- An OpenWeather API key: https://openweathermap.org/api
- Tkinter (included with most standard Python installers; on some Linux systems install `python3-tk`)

## 2. Setup

### macOS / Linux
Open Terminal in this folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENWEATHER_API_KEY="paste_your_api_key_here"
python weather_app.py
```

### Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENWEATHER_API_KEY="paste_your_api_key_here"
python weather_app.py
```

Replace `paste_your_api_key_here` with your own key from OpenWeather. Keep the key private; do not put it in GitHub or directly into source code. New keys may take some time to activate.

## 3. Use
Type a city or location in the search box (for example `Mumbai`, `London, UK`, or `New York, US`) and press **Search** or Enter. The app shows current conditions and forecast entries.

## 4. Common issues
- **API key missing:** Set `OPENWEATHER_API_KEY` in the same terminal/session used to launch the app.
- **401 Unauthorized:** The key may be wrong or not active yet.
- **404 Not Found:** Check the spelling and include a country code if a place name is ambiguous.
- **Connection error:** Check internet access.
- **Tkinter unavailable:** On Ubuntu/Debian run `sudo apt install python3-tk`.

## API endpoints
- Current weather: `https://api.openweathermap.org/data/2.5/weather`
- 5-day / 3-hour forecast: `https://api.openweathermap.org/data/2.5/forecast`

Temperature uses Celsius. Forecast values are representative 3-hour samples selected near midday for each date, not daily minimum/maximum predictions.
