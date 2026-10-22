
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Weather Data Analysis",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Weather Data Analysis System")
st.write("Analyze temperature, humidity, and rainfall.")

# Load weather data
df = pd.read_csv("weather_data.csv")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")
df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce")

df = df.dropna(subset=["date", "location"])

# Location selector
locations = sorted(df["location"].unique())
selected_location = st.selectbox("Select a location", locations)

filtered_df = df[df["location"] == selected_location].copy()

# Summary
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average Temperature",
    f"{filtered_df['temperature'].mean():.2f} °C"
)
col2.metric(
    "Highest Temperature",
    f"{filtered_df['temperature'].max():.2f} °C"
)
col3.metric(
    "Lowest Temperature",
    f"{filtered_df['temperature'].min():.2f} °C"
)
col4.metric(
    "Total Rainfall",
    f"{filtered_df['rainfall'].sum():.2f} mm"
)

# Prepare monthly data
filtered_df["month"] = filtered_df["date"].dt.strftime("%B")

monthly = filtered_df.groupby("month", sort=False).agg(
    average_temperature=("temperature", "mean"),
    total_rainfall=("rainfall", "sum")
)

st.subheader("📈 Monthly Average Temperature")

fig1, ax1 = plt.subplots()
ax1.plot(
    monthly.index,
    monthly["average_temperature"],
    marker="o"
)
ax1.set_xlabel("Month")
ax1.set_ylabel("Temperature (°C)")
ax1.grid(True)
plt.xticks(rotation=30)
st.pyplot(fig1)
plt.close(fig1)

st.subheader("🌧️ Monthly Rainfall")

fig2, ax2 = plt.subplots()
ax2.bar(monthly.index, monthly["total_rainfall"])
ax2.set_xlabel("Month")
ax2.set_ylabel("Rainfall (mm)")
plt.xticks(rotation=30)
st.pyplot(fig2)
plt.close(fig2)

st.subheader("📋 Weather Records")
st.dataframe(filtered_df, width="stretch")

st.subheader("🔎 Data Quality")
st.write("Missing values in the displayed records:")
st.dataframe(
    filtered_df[
        ["date", "location", "temperature", "humidity", "rainfall"]
    ].isnull().sum().rename("Missing Values")
)

st.caption(
    "This demonstration uses sample weather data, "
    "not verified live weather observations."
)

