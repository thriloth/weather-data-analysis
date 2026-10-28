
from flask import Flask, render_template, request
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import io
import base64
import requests
from datetime import date, timedelta
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

# Major Indian cities and their coordinates
CITIES = {
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Tirupati": (13.6288, 79.4192),
    "Mumbai": (19.0760, 72.8777),
    "New Delhi": (28.6139, 77.2090),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Kochi": (9.9312, 76.2673),
    "Visakhapatnam": (17.6868, 83.2185),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
    "Chandigarh": (30.7333, 76.7794),
    "Bhubaneswar": (20.2961, 85.8245),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Mysuru": (12.2958, 76.6394),
    "Mangaluru": (12.9141, 74.8560),
    "Vijayawada": (16.5062, 80.6480),
    "Warangal": (17.9689, 79.5941),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Dehradun": (30.3165, 78.0322),
    "Srinagar": (34.0837, 74.7973),
    "Amritsar": (31.6340, 74.8723),
    "Ranchi": (23.3441, 85.3096),
    "Guwahati": (26.1445, 91.7362),
    "Raipur": (21.2514, 81.6296),
    "Nagpur": (21.1458, 79.0882),
    "Surat": (21.1702, 72.8311),
    "Noida": (28.5355, 77.3910),
    "Gurugram": (28.4595, 77.0266),
    "Shimla": (31.1048, 77.1734),
    "Agra": (27.1767, 78.0081),
    "Varanasi": (25.3176, 82.9739),
    "Jodhpur": (26.2389, 73.0243),
    "Thane": (19.2183, 72.9781),
    "Nashik": (19.9975, 73.7898)
}

START_DATE = f"{date.today().year}-01-01"

# Historical archive is normally delayed by around five days.
END_DATE = min(
    date.today(),
    date.today() - timedelta(days=5)
).isoformat()


def fetch_weather(city, latitude, longitude):
    """Fetch daily historical weather for a location."""

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": (
            "temperature_2m_mean,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "relative_humidity_2m_mean,"
            "precipitation_sum"
        ),
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()

    if "daily" not in data:
        raise ValueError("The weather API did not return daily data.")

    daily = data["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "location": city,
        "temperature": daily["temperature_2m_mean"],
        "humidity": daily["relative_humidity_2m_mean"],
        "rainfall": daily["precipitation_sum"],
        "maximum_temperature": daily["temperature_2m_max"],
        "minimum_temperature": daily["temperature_2m_min"]
    })

    df["date"] = pd.to_datetime(df["date"])

    for column in [
        "temperature",
        "humidity",
        "rainfall",
        "maximum_temperature",
        "minimum_temperature"
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.dropna(subset=["date", "temperature"])


def make_chart(labels, values, title, ylabel, chart_type):
    fig, ax = plt.subplots(figsize=(9, 4))

    if chart_type == "line":
        ax.plot(labels, values, marker="o")
    else:
        ax.bar(labels, values)

    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis="x", rotation=30)

    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)

    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")


@app.route("/")
def home():
    city_name = request.args.get("city", "Bengaluru")
    search_query = request.args.get("search", "").strip()

    search_results = []
    error = None
    df = pd.DataFrame()

    # Search for a city in India
    if search_query:
        try:
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"

            geo_params = {
                "name": search_query,
                "count": 10,
                "language": "en",
                "countryCode": "IN"
            }

            response = requests.get(
                geo_url, params=geo_params, timeout=20
            )
            response.raise_for_status()

            results = response.json().get("results", [])

            for result in results:
                search_results.append({
                    "name": result["name"],
                    "admin1": result.get("admin1", ""),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"]
                })

            if not search_results:
                error = (
                    f"No matching Indian location found for "
                    f"'{search_query}'. Try another spelling."
                )

        except requests.RequestException:
            error = "Could not search locations. Check your internet connection."

    # Use coordinates from a search result, if provided
    custom_lat = request.args.get("lat")
    custom_lon = request.args.get("lon")
    custom_name = request.args.get("name")

    if custom_lat and custom_lon and custom_name:
        try:
            latitude = float(custom_lat)
            longitude = float(custom_lon)

            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError("Invalid coordinates")

            city_name = custom_name

        except (ValueError, TypeError):
            error = "Invalid location coordinates."

    elif city_name in CITIES:
        latitude, longitude = CITIES[city_name]
    else:
        city_name = "Bengaluru"
        latitude, longitude = CITIES[city_name]

    # Fetch weather when no search is in progress
    if not search_query and not error:
        try:
            df = fetch_weather(city_name, latitude, longitude)

            if df.empty:
                error = "No weather records were returned for this location."

        except requests.RequestException:
            error = (
                "Could not retrieve weather data. Check your internet "
                "connection and try again."
            )
        except (ValueError, KeyError) as exc:
            error = f"Could not process the weather data: {exc}"

    stats = None
    temperature_chart = None
    rainfall_chart = None
    records = []

    if not df.empty:
        stats = {
            "average": round(df["temperature"].mean(), 2),
            "highest": round(df["maximum_temperature"].max(), 2),
            "lowest": round(df["minimum_temperature"].min(), 2),
            "rainfall": round(df["rainfall"].sum(), 2),
            "humidity": round(df["humidity"].mean(), 2),
            "records": len(df)
        }

        df["month"] = df["date"].dt.to_period("M")

        monthly = df.groupby("month").agg(
            average_temperature=("temperature", "mean"),
            total_rainfall=("rainfall", "sum")
        )

        labels = monthly.index.strftime("%b %Y").tolist()

        temperature_chart = make_chart(
            labels,
            monthly["average_temperature"].tolist(),
            "Monthly Average Temperature",
            "Temperature (°C)",
            "line"
        )

        rainfall_chart = make_chart(
            labels,
            monthly["total_rainfall"].tolist(),
            "Monthly Total Rainfall",
            "Rainfall (mm)",
            "bar"
        )

        records_df = df.sort_values(
            "date", ascending=False
        ).head(100).copy()

        records_df["date"] = records_df["date"].dt.strftime("%Y-%m-%d")

        records = records_df.to_dict(orient="records")

        # Save the selected city's data locally
        df.drop(columns=["month"], errors="ignore").to_csv(
            BASE_DIR / "weather_data.csv", index=False
        )

    return render_template(
        "index.html",
        cities=sorted(CITIES.keys()),
        city_name=city_name,
        search_query=search_query,
        search_results=search_results,
        error=error,
        start_date=START_DATE,
        end_date=END_DATE,
        stats=stats,
        temperature_chart=temperature_chart,
        rainfall_chart=rainfall_chart,
        records=records
    )


if __name__ == "__main__":
    app.run(debug=True)

