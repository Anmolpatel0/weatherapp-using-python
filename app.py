"""Weather App with live OpenWeather API data.
Run: python weather_app.py
Requires: pip install -r requirements.txt
Get an API key from https://openweathermap.org/api and set OPENWEATHER_API_KEY.
"""
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import requests

API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
TIMEOUT_SECONDS = 12


def fetch_weather(city: str, api_key: str = API_KEY) -> dict:
    """Fetch current weather and 5-day/3-hour forecast for a city."""
    if not api_key:
        raise ValueError(
            "OpenWeather API key is missing. Set OPENWEATHER_API_KEY first. "
            "See README.md for instructions."
        )
    city = city.strip()
    if not city:
        raise ValueError("Please enter a city or location.")

    params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        current_response = requests.get(CURRENT_URL, params=params, timeout=TIMEOUT_SECONDS)
        if current_response.status_code == 401:
            raise ValueError("OpenWeather rejected the API key. Check that it is correct and active.")
        if current_response.status_code == 404:
            raise ValueError(f"Location '{city}' was not found. Try a city name such as 'London, UK'.")
        current_response.raise_for_status()
        current = current_response.json()

        forecast_response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT_SECONDS)
        if forecast_response.status_code == 401:
            raise ValueError("OpenWeather rejected the API key. Check that it is correct and active.")
        if forecast_response.status_code == 404:
            raise ValueError(f"Forecast location '{city}' was not found.")
        forecast_response.raise_for_status()
        forecast = forecast_response.json()
    except requests.Timeout as exc:
        raise RuntimeError("The weather service took too long to respond. Please try again.") from exc
    except requests.ConnectionError as exc:
        raise RuntimeError("Could not connect. Check your internet connection and try again.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise RuntimeError(f"Weather API request failed (HTTP {status}). Please try again later.") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Weather API request failed: {exc}") from exc

    return {"current": current, "forecast": forecast}


def format_results(data: dict) -> tuple[str, str]:
    current = data["current"]
    forecast = data["forecast"]
    name = current.get("name", "Unknown location")
    country = current.get("sys", {}).get("country", "")
    main = current.get("main", {})
    weather = (current.get("weather") or [{}])[0]
    wind = current.get("wind", {}).get("speed")
    location_line = f"{name}, {country}" if country else name
    current_lines = [
        location_line,
        f"Temperature: {main.get('temp', 'N/A')} °C (feels like {main.get('feels_like', 'N/A')} °C)",
        f"Condition: {weather.get('description', 'N/A').capitalize()}",
        f"Humidity: {main.get('humidity', 'N/A')}%",
        f"Pressure: {main.get('pressure', 'N/A')} hPa",
        f"Wind speed: {wind if wind is not None else 'N/A'} m/s",
    ]

    # OpenWeather's free 5-day forecast returns 3-hour intervals. Show one item
    # near midday for each date (or the first available item for that date).
    daily = {}
    for item in forecast.get("list", []):
        stamp = item.get("dt")
        if not stamp:
            continue
        day = datetime.fromtimestamp(stamp).strftime("%a, %d %b")
        hour = datetime.fromtimestamp(stamp).hour
        if day not in daily or abs(hour - 12) < abs(daily[day][0] - 12):
            daily[day] = (hour, item)

    forecast_lines = []
    for day, (_, item) in list(daily.items())[:5]:
        item_main = item.get("main", {})
        item_weather = (item.get("weather") or [{}])[0]
        forecast_lines.append(
            f"{day}: {item_main.get('temp', 'N/A')} °C — "
            f"{item_weather.get('description', 'N/A').capitalize()} "
            f"(humidity {item_main.get('humidity', 'N/A')}%)"
        )
    return "\\n".join(current_lines), "\\n".join(forecast_lines) or "Forecast data is unavailable."


class WeatherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Live Weather — OpenWeather")
        root.geometry("700x650")
        root.minsize(560, 520)
        root.configure(bg="#f3f6fb")

        title = tk.Label(root, text="Live Weather", font=("Arial", 24, "bold"),
                         bg="#f3f6fb", fg="#172554")
        title.pack(pady=(20, 4))
        subtitle = tk.Label(root, text="Search any city or location for current weather and forecast",
                            font=("Arial", 10), bg="#f3f6fb", fg="#475569")
        subtitle.pack(pady=(0, 16))

        search_frame = tk.Frame(root, bg="#f3f6fb")
        search_frame.pack(fill="x", padx=24)
        self.city_entry = tk.Entry(search_frame, font=("Arial", 13), relief="solid", bd=1)
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        self.city_entry.insert(0, "Mumbai")
        self.search_button = tk.Button(search_frame, text="Search", command=self.search,
                                       font=("Arial", 11, "bold"), bg="#2563eb", fg="white",
                                       activebackground="#1d4ed8", activeforeground="white",
                                       relief="flat", padx=18, pady=8, cursor="hand2")
        self.search_button.pack(side="right")
        self.city_entry.bind("<Return>", lambda _event: self.search())

        self.status = tk.Label(root, text="Enter a location and press Search.",
                               bg="#f3f6fb", fg="#64748b", anchor="w")
        self.status.pack(fill="x", padx=26, pady=(10, 4))

        self.current_box = tk.LabelFrame(root, text="Current conditions", font=("Arial", 11, "bold"),
                                         bg="white", fg="#172554", padx=14, pady=10)
        self.current_box.pack(fill="x", padx=24, pady=8)
        self.current_text = tk.Label(self.current_box, text="Weather details will appear here.",
                                     justify="left", anchor="w", bg="white", fg="#0f172a",
                                     font=("Arial", 12), wraplength=620)
        self.current_text.pack(fill="x")

        self.forecast_box = tk.LabelFrame(root, text="Forecast (up to 5 days)", font=("Arial", 11, "bold"),
                                          bg="white", fg="#172554", padx=14, pady=10)
        self.forecast_box.pack(fill="both", expand=True, padx=24, pady=(4, 16))
        self.forecast_text = tk.Label(self.forecast_box, text="Forecast will appear after a search.",
                                      justify="left", anchor="nw", bg="white", fg="#0f172a",
                                      font=("Arial", 11), wraplength=620)
        self.forecast_text.pack(fill="both", expand=True)

        self.root.after(300, self.search)

    def search(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Missing location", "Please type a city or location first.")
            return
        self.search_button.configure(state="disabled", text="Loading…")
        self.status.configure(text=f"Fetching live weather for {city}…", fg="#475569")
        self.root.update_idletasks()
        try:
            data = fetch_weather(city)
            current, forecast = format_results(data)
            self.current_text.configure(text=current)
            self.forecast_text.configure(text=forecast)
            self.status.configure(text="Updated with live OpenWeather data.", fg="#15803d")
        except (ValueError, RuntimeError) as exc:
            self.status.configure(text="Could not load weather.", fg="#b91c1c")
            messagebox.showerror("Weather lookup failed", str(exc))
        finally:
            self.search_button.configure(state="normal", text="Search")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
