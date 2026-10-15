# Weatherly — Streamlit Weather App

Responsive weather dashboard using Python, Streamlit, Requests, and OpenWeather API.

## Features
- Search for any city/location
- Current temperature, feels-like temperature, conditions
- Humidity, pressure, wind speed, visibility
- Up to five forecast days
- Error handling and 10-minute caching
- API key read securely from Streamlit Secrets or an environment variable

## Get an API key
Create one at https://openweathermap.org/api. Newly created keys may take time to activate. Keep the key private.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENWEATHER_API_KEY="paste_your_api_key_here"
streamlit run app.py
```
Open the local URL shown in Terminal, usually http://localhost:8501.

## Run on Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENWEATHER_API_KEY="paste_your_api_key_here"
streamlit run app.py
```

## Deploy a live preview with Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Create an app, select the repository and branch, and choose `app.py` as the main file.
4. In app settings, open **Secrets** and add:
```toml
OPENWEATHER_API_KEY = "paste_your_api_key_here"
```
5. Save and deploy. Share the resulting public URL on LinkedIn.

**Never commit your actual API key to GitHub.**

## API endpoints
- Current weather: `https://api.openweathermap.org/data/2.5/weather`
- Forecast: `https://api.openweathermap.org/data/2.5/forecast`

The forecast endpoint provides 3-hour intervals. This app selects the interval closest to midday per date; it does not claim to show daily high/low temperatures.
