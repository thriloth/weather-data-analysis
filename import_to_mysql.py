
import pandas as pd
import mysql.connector

# Load weather data from CSV
df = pd.read_csv("weather_data.csv")

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mbu@2026",
    database="weather_db"
)

cursor = connection.cursor()

# SQL query to insert weather records
query = """
INSERT INTO weather_records
(observation_date, location, temperature, humidity, rainfall)
VALUES (%s, %s, %s, %s, %s)
"""

# Prepare the data
records = []

for _, row in df.iterrows():
    records.append((
        pd.to_datetime(row["date"]).date(),
        row["location"],
        float(row["temperature"]),
        float(row["humidity"]),
        float(row["rainfall"])
    ))

# Insert all records
cursor.executemany(query, records)

# Save changes
connection.commit()

print("Weather data imported successfully!")
print("Records inserted:", cursor.rowcount)

# Close the connection
cursor.close()
connection.close()

