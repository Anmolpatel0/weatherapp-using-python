import pandas as pd
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Live Weather Dashboard", page_icon="🌤️", layout="centered"
)

# Custom Aesthetic Styling injected via Python
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: white;
        border-radius: 10px;
        border: 1px solid #3b82f6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# App Title & Header
st.title("🌤️ Live Weather Dashboard")
st.markdown(
    "A gorgeous, high-performance web application built **entirely in Python**"
    " using Streamlit & OpenWeather API."
)

# Sidebar Configuration for API Key
st.sidebar.header("⚙️ App Settings")
api_key_input = st.sidebar.text_input(
    "OpenWeather API Key",
    type="password",
    value="",
    help=(
        "Enter your OpenWeatherMap API key here. Leave blank for Demo mode."
    ),
)
default_city = st.sidebar.text_input("Default Search City", value="London")

# Search Section in Main UI
col1, col2 = st.columns([3, 1])
with col1:
  city = st.text_input(
      "Enter City Name",
      value=default_city,
      placeholder="Type city (e.g., Tokyo, Paris, Delhi)...",
  )
with col2:
  st.markdown("<br>", unsafe_allow_html=True)
  search_clicked = st.button("🔍 Search", use_container_width=True)

# API Endpoints
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

if city:
  api_key = api_key_input if api_key_input else "YOUR_OPENWEATHER_API_KEY"

  # Fallback to Demo Mode if API Key is not provided
  if api_key == "YOUR_OPENWEATHER_API_KEY":
    st.info(
        "💡 Running in **Demo Mode**. Enter your OpenWeather API Key in the"
        " sidebar for live data!"
    )
    data = {
        "name": city.capitalize(),
        "sys": {"country": "IN"},
        "main": {
            "temp": 28.5,
            "feels_like": 30.2,
            "humidity": 55,
            "pressure": 1010,
        },
        "weather": [{"description": "clear sky"}],
        "wind": {"speed": 3.6},
    }

    st.subheader(
        f"📍 Current Weather in {data['name']}, {data['sys']['country']}"
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temperature", f"{data['main']['temp']} °C", "Feels like 30.2°C")
    m2.metric("Humidity", f"{data['main']['humidity']} %")
    m3.metric("Wind Speed", f"{data['wind']['speed']} m/s")
    m4.metric("Pressure", f"{data['main']['pressure']} hPa")

    st.success(
        f"☁️ Condition: {data['weather'][0]['description'].capitalize()}"
    )

    # Demo Chart
    st.subheader("📈 5-Day Temperature Trend")
    chart_df = pd.DataFrame(
        {
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "Temp (°C)": [26, 28, 29, 27, 30],
        }
    )
    st.line_chart(chart_df, x="Day", y="Temp (°C)", color="#3b82f6")

  else:
    try:
      params = {"q": city, "appid": api_key, "units": "metric"}
      response = requests.get(CURRENT_URL, params=params, timeout=10)

      if response.status_code == 404:
        st.error(
            f"❌ City '{city}' not found. Please check your spelling and try"
            " again."
        )
      elif response.status_code == 401:
        st.error(
            "❌ Invalid API Key. Please verify your OpenWeather credentials."
        )
      else:
        response.raise_for_status()
        data = response.json()

        st.subheader(
            f"📍 Current Weather in {data['name']}, {data['sys']['country']}"
        )

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        condition = data["weather"][0]["description"].capitalize()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Temperature", f"{temp:.1f} °C", f"Feels like {feels_like:.1f}°C"
        )
        m2.metric("Humidity", f"{humidity} %")
        m3.metric("Wind Speed", f"{wind_speed} m/s")
        m4.metric("Pressure", f"{pressure} hPa")

        st.success(f"☁️ Condition: {condition}")

        # Fetch 5-Day Forecast Data
        forecast_res = requests.get(FORECAST_URL, params=params, timeout=10)
        if forecast_res.status_code == 200:
          forecast_data = forecast_res.json()
          dates, temps = [], []
          for item in forecast_data["list"][::8]:  # Daily intervals
            dates.append(item["dt_txt"].split(" ")[0])
            temps.append(item["main"]["temp"])

          st.subheader("📈 5-Day Temperature Forecast")
          df_forecast = pd.DataFrame({"Date": dates, "Temp (°C)": temps})
          st.line_chart(df_forecast, x="Date", y="Temp (°C)", color="#3b82f6")

    except requests.exceptions.ConnectionError:
      st.error(
          "🌐 Network error! Please check your internet connection and try"
          " again."
      )
    except Exception as e:
      st.error(f"⚠️ An unexpected error occurred: {e}")
