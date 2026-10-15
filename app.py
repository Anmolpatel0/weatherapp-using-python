import os
from datetime import datetime
import requests
import streamlit as st

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
TIMEOUT = 12

st.set_page_config(page_title="Weatherly — Live Weather", page_icon="🌦️", layout="wide")
st.markdown("""
<style>
.stApp{background:radial-gradient(circle at top right,#193b67 0,#0b1730 40%,#081225 100%);color:#f8fafc}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1150px;padding-top:2rem;padding-bottom:3rem}
.hero{padding:1rem 0}.eyebrow{color:#8dbbff;font-size:.8rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase}
.hero-title{color:#f8fafc;font-size:clamp(2rem,4vw,3.1rem);font-weight:800;line-height:1.1;margin:.35rem 0}
.hero-sub,.muted{color:#a9bad3}
.weather-card{border:1px solid #35577e;border-radius:22px;padding:1.4rem 1.5rem;background:linear-gradient(135deg,#1c4577,#0d1f3b);min-height:220px}
.city{color:#f8fafc;font-size:1.5rem;font-weight:750}.temperature{color:white;font-size:clamp(3.4rem,7vw,5.4rem);font-weight:800;line-height:1.05}
.condition{color:#dbeafe;font-size:1.1rem;text-transform:capitalize}
.metric{background:#0f2240;border:1px solid #263f61;padding:1rem;border-radius:16px;min-height:105px}
.metric-label{color:#9db2cf;font-size:.88rem}.metric-value{color:#f8fafc;font-size:1.4rem;font-weight:750;margin-top:.25rem}
.section-title{color:#f8fafc;font-size:1.35rem;font-weight:750;margin:1.25rem 0 .7rem}
.forecast-card{background:#0d1f3b;border:1px solid #263f61;border-radius:17px;padding:1rem .5rem;text-align:center;height:100%}
.forecast-day{color:#e2e8f0;font-weight:700}.forecast-icon{font-size:2rem;padding:.45rem 0}
.forecast-temp{color:white;font-size:1.2rem;font-weight:750}.forecast-desc{color:#9db2cf;font-size:.85rem;text-transform:capitalize;min-height:2.3rem}
div[data-testid="stForm"]{background:#102546;border:1px solid #263f61;padding:1rem;border-radius:18px}
.footer{color:#8296b4;text-align:center;font-size:.85rem;padding-top:2rem}
</style>""", unsafe_allow_html=True)

def api_key():
    try:
        secret = st.secrets.get("OPENWEATHER_API_KEY", "")
    except Exception:
        secret = ""
    return str(secret or os.getenv("OPENWEATHER_API_KEY", "")).strip()

@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(city, key):
    params = {"q": city.strip(), "appid": key, "units": "metric"}
    try:
        r = requests.get(CURRENT_URL, params=params, timeout=TIMEOUT)
        if r.status_code == 401:
            raise ValueError("OpenWeather rejected the API key. Check that it is correct and active.")
        if r.status_code == 404:
            raise ValueError(f"Location '{city}' was not found. Try a more specific name, e.g. London, UK.")
        r.raise_for_status()
        current = r.json()
        r = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
        if r.status_code == 401:
            raise ValueError("OpenWeather rejected the API key. Check that it is correct and active.")
        r.raise_for_status()
        return {"current": current, "forecast": r.json()}
    except requests.Timeout as exc:
        raise RuntimeError("The weather service timed out. Please try again.") from exc
    except requests.ConnectionError as exc:
        raise RuntimeError("Could not connect. Check your internet connection.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise RuntimeError(f"Weather API request failed (HTTP {status}).") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Weather API request failed: {exc}") from exc

def emoji(description):
    d = description.lower()
    if "thunder" in d: return "⛈️"
    if "snow" in d: return "❄️"
    if "rain" in d or "drizzle" in d: return "🌧️"
    if "cloud" in d: return "☁️"
    if any(x in d for x in ("mist", "fog", "haze")): return "🌫️"
    if "clear" in d: return "☀️"
    return "🌤️"

def daily_forecast(data):
    chosen = {}
    for item in data.get("list", []):
        stamp = item.get("dt")
        if not stamp: continue
        dt = datetime.fromtimestamp(stamp)
        key = dt.strftime("%Y-%m-%d")
        if key not in chosen or abs(dt.hour - 12) < abs(chosen[key][0] - 12):
            chosen[key] = (dt.hour, item)
    days = []
    for key, (_, item) in list(chosen.items())[:5]:
        dt = datetime.strptime(key, "%Y-%m-%d")
        desc = (item.get("weather") or [{}])[0].get("description", "Unavailable")
        days.append({"day": dt.strftime("%a"), "date": dt.strftime("%d %b"),
                     "temp": item.get("main", {}).get("temp"),
                     "humidity": item.get("main", {}).get("humidity"),
                     "description": desc, "icon": emoji(desc)})
    return days

def metric(label, value, symbol):
    st.markdown(f'<div class="metric"><div class="metric-label">{symbol} &nbsp;{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">Live conditions · Forecast · OpenWeather</div><div class="hero-title">Weather, made clear. 🌦️</div><div class="hero-sub">Real-time weather details for the places that matter to you.</div></div>', unsafe_allow_html=True)
with st.form("weather_search"):
    c1, c2 = st.columns([5, 1])
    with c1:
        city = st.text_input("Search a city or location", value=st.session_state.get("last_city", "Mumbai"), placeholder="Mumbai, London, New York")
    with c2:
        st.markdown("<div style='height:1.72rem'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🔎 Search", use_container_width=True)
if submitted:
    st.session_state["last_city"] = city.strip()

key = api_key()
if not key:
    st.warning("Add your OpenWeather API key to enable live weather searches.")
    st.markdown("Get a key at [OpenWeather API](https://openweathermap.org/api). For Streamlit Cloud, open **App settings → Secrets** and add:")
    st.code('OPENWEATHER_API_KEY = "paste_your_key_here"', language="toml")
else:
    selected = st.session_state.get("last_city", city).strip()
    if not selected:
        st.info("Enter a city or location to search.")
    else:
        try:
            with st.spinner(f"Fetching live weather for {selected}..."):
                data = fetch_weather(selected, key)
            current = data["current"]
            main = current.get("main", {})
            sys_data = current.get("sys", {})
            desc = (current.get("weather") or [{}])[0].get("description", "Unavailable")
            place = current.get("name", selected)
            country = sys_data.get("country", "")
            place = f"{place}, {country}" if country else place
            wind = current.get("wind", {}).get("speed")
            wind = f"{wind * 3.6:.1f} km/h" if isinstance(wind, (int, float)) else "N/A"

            left, right = st.columns([1.2, 1])
            with left:
                st.markdown(f"""<div class="weather-card"><div class="city">📍 {place}</div><div class="muted">Current weather</div><div style="display:flex;align-items:center;gap:1rem;margin-top:.9rem"><div style="font-size:4rem">{emoji(desc)}</div><div><div class="temperature">{round(main.get('temp', 0))}°C</div><div class="condition">{desc}</div></div></div><div class="muted" style="margin-top:.7rem">Feels like {round(main.get('feels_like', 0))}°C</div></div>""", unsafe_allow_html=True)
            with right:
                st.markdown('<div class="section-title" style="margin-top:0">Weather details</div>', unsafe_allow_html=True)
                a, b = st.columns(2)
                with a: metric("Humidity", f"{main.get('humidity', 'N/A')}%", "💧")
                with b: metric("Wind speed", wind, "💨")
                a, b = st.columns(2)
                with a: metric("Pressure", f"{main.get('pressure', 'N/A')} hPa", "🧭")
                with b:
                    visibility = current.get("visibility")
                    metric("Visibility", f"{visibility / 1000:.1f} km" if isinstance(visibility, (int, float)) else "N/A", "👁️")

            st.markdown('<div class="section-title">📅 5-day forecast</div>', unsafe_allow_html=True)
            days = daily_forecast(data["forecast"])
            if days:
                cols = st.columns(len(days))
                for col, day in zip(cols, days):
                    temp = round(day["temp"]) if isinstance(day["temp"], (int, float)) else "—"
                    with col:
                        st.markdown(f"""<div class="forecast-card"><div class="forecast-day">{day['day']}</div><div class="muted">{day['date']}</div><div class="forecast-icon">{day['icon']}</div><div class="forecast-temp">{temp}°C</div><div class="forecast-desc">{day['description']}</div><div class="muted" style="font-size:.8rem">💧 {day['humidity']}%</div></div>""", unsafe_allow_html=True)
            else:
                st.info("Forecast data is not available.")
            st.caption("Forecast uses the 3-hour interval nearest midday for each date; values are not daily high/low predictions.")
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
        except Exception:
            st.error("Something unexpected happened. Check the location and try again.")

st.markdown('<div class="footer">Built with Python & Streamlit · Weather data by OpenWeather · Keep your API key private</div>', unsafe_allow_html=True)
