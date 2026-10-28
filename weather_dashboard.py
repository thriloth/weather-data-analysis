
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mbu@2026",
    database="weather_db"
)

# Retrieve data
query = "SELECT * FROM weather_records"
df = pd.read_sql(query, connection)

connection.close()

# Calculate statistics
avg_temp = df["temperature"].mean()
max_temp = df["temperature"].max()
min_temp = df["temperature"].min()
total_rainfall = df["rainfall"].sum()

print("\n========== WEATHER DASHBOARD ==========")
print(f"Average Temperature: {avg_temp:.2f} °C")
print(f"Highest Temperature: {max_temp:.2f} °C")
print(f"Lowest Temperature: {min_temp:.2f} °C")
print(f"Total Rainfall: {total_rainfall:.2f} mm")

# Prepare monthly data
df["observation_date"] = pd.to_datetime(df["observation_date"])
df["month"] = df["observation_date"].dt.strftime("%B")

monthly = df.groupby("month", sort=False).agg(
    average_temperature=("temperature", "mean"),
    total_rainfall=("rainfall", "sum")
)

# Temperature chart
plt.figure(figsize=(9, 5))
plt.bar(monthly.index, monthly["average_temperature"])
plt.title("Monthly Average Temperature")
plt.xlabel("Month")
plt.ylabel("Temperature (°C)")
plt.tight_layout()
plt.savefig("dashboard_temperature.png")
plt.show()

# Rainfall chart
plt.figure(figsize=(9, 5))
plt.bar(monthly.index, monthly["total_rainfall"])
plt.title("Monthly Rainfall")
plt.xlabel("Month")
plt.ylabel("Rainfall (mm)")
plt.tight_layout()
plt.savefig("dashboard_rainfall.png")
plt.show()

print("\nDashboard charts saved successfully!")

