from kafka import KafkaProducer
from faker import Faker
import json
import time
import random
import os
import signal
import sys
from dotenv import load_dotenv
from datetime import datetime

# Fix the load_dotenv call
load_dotenv('config/.env')

# Load environment variables
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iot-medical")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

DEVICE_IDS = [
    "ICU-MONITOR-A121",
    "VITALS-PRO-B235",
    "CARDIO-TRACK-C344",
    "TEMP-SENSE-D417",
    "BP-MONITOR-E528",
    "SPO2-SCAN-F639",
    "PATIENT-MON-G742",
    "MULTI-PARAM-H853",
    "RESP-TRACK-I964",
    "TELE-VITALS-J075"
]

# set Faker
fake = Faker()

# JSON serializer
def convert_to_kafka_format(data):
    # Step 1: Convert python dictionary to JSON string
    json_data = json.dumps(data, indent=4, sort_keys=True, 
                          separators=(',', ': '), ensure_ascii=False)
    # Step 2: Convert JSON string to bytes
    byte_data = json_data.encode('utf-8')
    return byte_data

# Function to generate fake IoT data
def generate_data():
    current_time = fake.date_time_this_month()
    return {
        # Device information
        "device_id": random.choice(DEVICE_IDS),
        "device_type": "patient_monitor",
        "firmware_version": f"v{random.choice(['1.2.3', '1.3.0', '2.0.1'])}",
        
        # Timestamps
        "timestamp": datetime.utcnow().isoformat(),
        "reading_interval_sec": 60,
        
        # Patient identifiers
        "patient_id": f"P{random.randint(1, 100)}",
        "hospital_room": f"{random.choice(['ICU', 'ER', 'Ward'])}-{random.randint(1, 20)}",
        
        # Vital signs
        "heart_rate": random.randint(40, 150),
        "heart_rate_variability": round(random.uniform(10, 50), 1),
        "temperature": round(random.uniform(36.0, 40.5), 1),
        "temperature_location": random.choice(["oral", "axillary", "tympanic"]),
        "spo2": random.randint(92, 100),
        "blood_pressure": {
            "systolic": random.randint(90, 180),
            "diastolic": random.randint(60, 110)
        },
        "respiratory_rate": random.randint(12, 25),
        
        # Status indicators
        "battery_level": random.randint(10, 100),
        "signal_strength": random.randint(1, 5),
        "alarm_status": random.choice([None, "low", "medium", "high"]),
        
        # Alerts
        "alerts": random.choice([
            [],
            ["low_battery"],
            ["abnormal_heart_rate"],
            ["abnormal_heart_rate", "fever"]
        ]),
        
        # Calculated values
        "perfusion_index": round(random.uniform(0.5, 5.0), 2),
        "mean_arterial_pressure": random.randint(70, 110)
    }

# Initialize the producer
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=convert_to_kafka_format,
        key_serializer=convert_to_kafka_format
    )
    print(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    sys.exit(1)

# Handler for graceful shutdown for Data Integrity and Loss Prevention
def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    # Flush any pending messages
    producer.flush()
    # Close the producer connection
    producer.close()
    print("Producer closed. Exiting.")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)  # Handles Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handles termination signal

print(f"Starting IoT medical data producer. Press Ctrl+C to stop.")
# Main loop with error handling
try:
    message_count = 0
    while True:
        try:
            reading = generate_data()
            # Include the device_id as the key for partitioning
            key = reading["device_id"]
            future = producer.send(KAFKA_TOPIC, key=key, value=reading)
            # Wait for the message to be delivered
            record_metadata = future.get(timeout=10)
            message_count += 1
            
            if message_count % 10 == 0:
                print(f"Sent {message_count} messages. Last message: {reading['device_id']} - {reading['timestamp']}")
            
            time.sleep(1)
        except Exception as e:
            print(f"Error sending message: {e}")
            time.sleep(5)  # Wait before retrying
except KeyboardInterrupt:
    # This is caught by the signal handler
    pass
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Make sure resources are closed even if an unexpected error occurs
    if producer:
        producer.flush()
        producer.close()
        print("Producer closed. Exiting.")