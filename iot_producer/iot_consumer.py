from kafka import KafkaConsumer
import psycopg2
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import signal
import sys

load_dotenv('config/.env')

# Kafka config
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iot-medical")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# PostgreSQL config
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "airflow")
PG_USER = os.getenv("PG_USER", "airflow")
PG_PASS = os.getenv("PG_PASS", "airflow")

# PostgreSQL connection
conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASS
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS iot_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    device_id TEXT,
    patient_id TEXT,
    heart_rate INT,
    temperature FLOAT,
    spo2 INT,
    respiratory_rate INT,
    systolic INT,
    diastolic INT
);
""")
conn.commit()

def value_deserializer(value):
    try:
        return json.loads(value.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return None
    
# Kafka consumer setup
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=value_deserializer,
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

print(f"Listening to Kafka topic: {KAFKA_TOPIC}")

def graceful_shutdown(sig, frame):
    print("\nShutting down gracefully...")
    consumer.close()
    cursor.close()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

# Process messages with timeout
try:
    for msg in consumer:
        data = msg.value
        try:
            cursor.execute("""
                INSERT INTO iot_readings (
                    timestamp, device_id, patient_id,
                    heart_rate, temperature, spo2,
                    respiratory_rate, systolic, diastolic
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data.get("timestamp"),
                data.get("device_id"),
                data.get("patient_id"),
                data.get("heart_rate"),
                data.get("temperature"),
                data.get("spo2"),
                data.get("respiratory_rate"),
                data.get("blood_pressure", {}).get("systolic"),
                data.get("blood_pressure", {}).get("diastolic")
            ))
            conn.commit()
            print(f"Inserted record from device {data.get('device_id')} at {data.get('timestamp')}")
        except Exception as e:
            print(f"Error inserting data: {e}")
except Exception as e:
    print(f"Error in consumer loop: {e}")
