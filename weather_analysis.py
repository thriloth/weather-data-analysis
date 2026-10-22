import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("===================================")
print("   WEATHER DATA ANALYSIS SYSTEM")
print("===================================")

# Step 1: Load weather data
df = pd.read_csv("weather_data.csv")

# Step 2: Convert columns to correct data types
df["date"] = pd.to_datetime(df["date"], errors="coerce")

for col in ["temperature", "humidity", "rainfall"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Step 3: Remove rows with invalid dates
df = df.dropna(subset=["date"])

# Step 4: Create a month column
df["month"] = df["date"].dt.to_period("M")

# Step 5: Calculate monthly statistics
monthly_summary = df.groupby(["location", "month"]).agg(
    average_temperature=("temperature", "mean"),
    maximum_temperature=("temperature", "max"),
    minimum_temperature=("temperature", "min"),
    average_humidity=("humidity", "mean"),
    total_rainfall=("rainfall", "sum")
).reset_index()

# Step 6: Display the results
print("\nMONTHLY WEATHER SUMMARY")
print(monthly_summary.round(2).to_string(index=False))

# Step 7: Save the summary to a CSV file
monthly_summary.to_csv("monthly_summary.csv", index=False)

print("\nMonthly summary saved successfully!")


# STEP 10: WEATHER VISUALIZATION

# Graph 1: Temperature Trend

plt.figure(figsize=(10, 5))

for location in df["location"].dropna().unique():
    location_data = df[df["location"] == location]

    plt.plot(
        location_data["date"],
        location_data["temperature"],
        marker="o",
        label=location
    )

plt.title("Weather Temperature Trend")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("temperature_trend.png")
plt.show()


# Graph 2: Monthly Rainfall Comparison

rainfall_data = monthly_summary.copy()
rainfall_data["month"] = rainfall_data["month"].astype(str)

for location in rainfall_data["location"].unique():
    location_data = rainfall_data[
        rainfall_data["location"] == location
    ]

    plt.figure(figsize=(8, 5))

    plt.bar(
        location_data["month"],
        location_data["total_rainfall"]
    )

    plt.title(f"Monthly Rainfall Comparison - {location}")
    plt.xlabel("Month")
    plt.ylabel("Rainfall (mm)")
    plt.grid(axis="y")
    plt.tight_layout()

    plt.savefig(f"rainfall_{location}.png")
    plt.show()

print("\nWeather graphs created successfully!")



# STEP 11: DATA VALIDATION

print("\n===================================")
print("       DATA QUALITY REPORT")
print("===================================")

# Check missing values in the original columns
print("\nMissing values:")
print(df[[
    "date",
    "location",
    "temperature",
    "humidity",
    "rainfall"
]].isnull().sum())

# Check invalid temperature values
invalid_temperature = df[
    (df["temperature"] < -90) |
    (df["temperature"] > 60)
]

print("\nInvalid temperature records:")
print(invalid_temperature)

# Check invalid humidity values
invalid_humidity = df[
    (df["humidity"] < 0) |
    (df["humidity"] > 100)
]

print("\nInvalid humidity records:")
print(invalid_humidity)

# Check negative rainfall
invalid_rainfall = df[df["rainfall"] < 0]

print("\nInvalid rainfall records:")
print(invalid_rainfall)

# Save the data quality report
quality_report = pd.DataFrame({
    "Check": [
        "Missing values",
        "Invalid temperature records",
        "Invalid humidity records",
        "Negative rainfall records"
    ],
    "Count": [
        int(df[[
            "date", "location", "temperature",
            "humidity", "rainfall"
        ]].isnull().sum().sum()),
        len(invalid_temperature),
        len(invalid_humidity),
        len(invalid_rainfall)
    ]
})

quality_report.to_csv(
    "data_quality_report.csv",
    index=False
)

print("\nData quality report saved successfully!")



