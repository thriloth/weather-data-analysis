import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import date, timedelta

st.set_page_config(
    page_title="India Weather Analytics",
    page_icon="🌦️",
    layout="wide"
)

st.title("🇮🇳 India Weather Data Analysis")
st.write(
    "Explore historical weather data for cities across India in 2026."
)

st.info(
    "Search for a city, choose a date range, and explore "
    "temperature, rainfall, humidity, and wind speed."
)

# Historical data can have a reporting delay.
today = date.today()
latest_available_date = today - timedelta(days=5)

start_default = date(today.year, 1, 1)
end_default = min(latest_available_date, today)

if end_default < start_default:
    st.error("The selected year does not have available historical dates yet.")
    st.stop()

# Search for Indian cities
st.subheader("🔍 Search for an Indian city")

city_name = st.text_input(
    "Enter a city name",
    placeholder="Example: Bengaluru, Hyderabad, Mumbai"
)

@st.cache_data(ttl=3600)
def search_cities(name):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    response = requests.get(
        url,
        params={
            "name": name,
            "count": 20,
            "language": "en",
            "format": "json"
        },
        timeout=20
    )
    response.raise_for_status()

    results = response.json().get("results", [])

    # Keep locations in India only
    return [
        city for city in results
        if city.get("country_code") == "IN"
    ]


if city_name.strip():
    try:
        cities = search_cities(city_name.strip())

        if not cities:
            st.warning(
                "No matching Indian city found. "
                "Try another spelling or city name."
            )
            st.stop()

        city_labels = [
            (
                f"{city['name']}, "
                f"{city.get('admin1', 'India')} "
                f"({city['latitude']:.3f}, "
                f"{city['longitude']:.3f})"
            )
            for city in cities
        ]

        selected_label = st.selectbox(
            "Select a matching location",
            city_labels
        )

        selected_index = city_labels.index(selected_label)
        selected_city = cities[selected_index]

        st.subheader(f"📍 {selected_city['name']}")

        st.caption(
            f"Latitude: {selected_city['latitude']} | "
            f"Longitude: {selected_city['longitude']}"
        )

        # Date selection
        date_range = st.date_input(
            "Choose the date range",
            value=(start_default, end_default),
            min_value=date(today.year, 1, 1),
            max_value=end_default
        )

        if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
            st.info("Please select both a start date and an end date.")
            st.stop()

        start_date, end_date = date_range

        if start_date > end_date:
            st.error("Start date must be before the end date.")
            st.stop()

        # Retrieve historical weather data
        if st.button("Get Weather Data", type="primary"):

            with st.spinner("Fetching historical weather data..."):

                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": selected_city["latitude"],
                    "longitude": selected_city["longitude"],
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "daily": (
                        "temperature_2m_max,"
                        "temperature_2m_min,"
                        "temperature_2m_mean,"
                        "precipitation_sum,"
                        "wind_speed_10m_max"
                    ),
                    "hourly": "relative_humidity_2m",
                    "timezone": "auto"
                }

                try:
                    response = requests.get(
                        url,
                        params=params,
                        timeout=60
                    )
                    response.raise_for_status()
                    weather = response.json()

                    if "daily" not in weather:
                        st.error(
                            "Weather data is unavailable for this "
                            "location or date range."
                        )
                        st.stop()

                    daily = weather["daily"]

                    df = pd.DataFrame({
                        "Date": daily["time"],
                        "Maximum Temperature (°C)": (
                            daily["temperature_2m_max"]
                        ),
                        "Minimum Temperature (°C)": (
                            daily["temperature_2m_min"]
                        ),
                        "Average Temperature (°C)": (
                            daily["temperature_2m_mean"]
                        ),
                        "Rainfall (mm)": daily["precipitation_sum"],
                        "Maximum Wind Speed (km/h)": (
                            daily["wind_speed_10m_max"]
                        )
                    })

                    df["Date"] = pd.to_datetime(df["Date"])

                    # Calculate daily average humidity from hourly data
                    hourly = weather.get("hourly", {})

                    if (
                        hourly.get("time")
                        and hourly.get("relative_humidity_2m")
                    ):
                        humidity_df = pd.DataFrame({
                            "Date": pd.to_datetime(hourly["time"]),
                            "Humidity (%)": (
                                hourly["relative_humidity_2m"]
                            )
                        })

                        humidity_df["Date"] = (
                            humidity_df["Date"].dt.date
                        )

                        humidity_daily = (
                            humidity_df.groupby("Date")["Humidity (%)"]
                            .mean()
                            .reset_index()
                        )

                        humidity_daily["Date"] = pd.to_datetime(
                            humidity_daily["Date"]
                        )

                        df = df.merge(
                            humidity_daily,
                            on="Date",
                            how="left"
                        )
                    else:
                        df["Humidity (%)"] = float("nan")

                    st.success("Weather data loaded successfully!")

                    # Summary cards
                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric(
                        "Average Temperature",
                        f"{df['Average Temperature (°C)'].mean():.1f} °C"
                    )

                    col2.metric(
                        "Highest Temperature",
                        f"{df['Maximum Temperature (°C)'].max():.1f} °C"
                    )

                    col3.metric(
                        "Total Rainfall",
                        f"{df['Rainfall (mm)'].sum():.1f} mm"
                    )

                    col4.metric(
                        "Average Humidity",
                        (
                            f"{df['Humidity (%)'].mean():.1f}%"
                            if df["Humidity (%)"].notna().any()
                            else "Unavailable"
                        )
                    )

                    # Temperature chart
                    st.subheader("🌡️ Temperature Analysis")

                    fig, ax = plt.subplots(figsize=(12, 5))

                    ax.plot(
                        df["Date"],
                        df["Maximum Temperature (°C)"],
                        label="Maximum"
                    )

                    ax.plot(
                        df["Date"],
                        df["Minimum Temperature (°C)"],
                        label="Minimum"
                    )

                    ax.plot(
                        df["Date"],
                        df["Average Temperature (°C)"],
                        label="Average"
                    )

                    ax.set_xlabel("Date")
                    ax.set_ylabel("Temperature (°C)")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    fig.autofmt_xdate()

                    st.pyplot(fig)
                    plt.close(fig)

                    # Rainfall chart
                    st.subheader("🌧️ Rainfall Analysis")

                    fig, ax = plt.subplots(figsize=(12, 4))

                    ax.bar(
                        df["Date"],
                        df["Rainfall (mm)"]
                    )

                    ax.set_xlabel("Date")
                    ax.set_ylabel("Rainfall (mm)")
                    ax.grid(axis="y", alpha=0.3)
                    fig.autofmt_xdate()

                    st.pyplot(fig)
                    plt.close(fig)

                    # Humidity chart
                    st.subheader("💧 Humidity Analysis")

                    if df["Humidity (%)"].notna().any():
                        fig, ax = plt.subplots(figsize=(12, 4))

                        ax.plot(
                            df["Date"],
                            df["Humidity (%)"]
                        )

                        ax.set_xlabel("Date")
                        ax.set_ylabel("Humidity (%)")
                        ax.grid(True, alpha=0.3)
                        fig.autofmt_xdate()

                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.info("Humidity data is unavailable.")

                    # Wind chart
                    st.subheader("💨 Wind Speed Analysis")

                    fig, ax = plt.subplots(figsize=(12, 4))

                    ax.plot(
                        df["Date"],
                        df["Maximum Wind Speed (km/h)"]
                    )

                    ax.set_xlabel("Date")
                    ax.set_ylabel("Wind Speed (km/h)")
                    ax.grid(True, alpha=0.3)
                    fig.autofmt_xdate()

                    st.pyplot(fig)
                    plt.close(fig)

                    # Data table
                    st.subheader("📊 Historical Weather Records")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # CSV download
                    csv_data = df.to_csv(index=False).encode("utf-8")

                    st.download_button(
                        label="📥 Download Weather Data as CSV",
                        data=csv_data,
                        file_name=(
                            f"{selected_city['name']}_weather_2026.csv"
                        ),
                        mime="text/csv"
                    )

                    st.caption(
                        "Source: Open-Meteo Historical Weather API. "
                        "Values represent model-based weather data "
                        "and may differ from local weather station "
                        "observations."
                    )

                except requests.RequestException as error:
                    st.error(
                        "Unable to retrieve weather data. "
                        "Please try again later."
                    )
                    st.caption(str(error))

    except requests.RequestException:
        st.error(
            "Unable to search for cities. "
            "Check your internet connection and try again."
        )

else:
    st.markdown(
        """
        ### How to use this dashboard

        1. Enter an Indian city in the search box.
        2. Select the matching location.
        3. Choose a date range in 2026.
        4. Click **Get Weather Data**.
        5. Explore the charts and download the results.
        """
    )

st.divider()

st.caption(
    "India Weather Data Analysis | Built with Python, "
    "Pandas, Matplotlib, Requests and Streamlit"
)
