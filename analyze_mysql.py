
import pandas as pd
import mysql.connector

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mbu@2026",
    database="weather_db"
)

# Read weather data from MySQL
query = "SELECT * FROM weather_records"

df = pd.read_sql(query, connection)

# Display all records
print("\nWEATHER RECORDS")
print(df)

# Calculate statistics
print("\nWEATHER STATISTICS")
print("Average Temperature:", round(df["temperature"].mean(), 2), "°C")
print("Highest Temperature:", df["temperature"].max(), "°C")
print("Lowest Temperature:", df["temperature"].min(), "°C")
print("Total Rainfall:", df["rainfall"].sum(), "mm")

# Display location-wise statistics
print("\nLOCATION-WISE ANALYSIS")
summary = df.groupby("location").agg(
    average_temperature=("temperature", "mean"),
    highest_temperature=("temperature", "max"),
    lowest_temperature=("temperature", "min"),
    total_rainfall=("rainfall", "sum")
)

print(summary.round(2))

# Close connection
connection.close()

