import pymysql
import paho.mqtt.client as mqtt
from time import sleep

conn = pymysql.connect(
    host='127.0.0.1',
    unix_socket='/var/run/mysqld/mysqld.sock',
    user='Smets',
    passwd='Thomas',
    db='MQTT'
)
cur = conn.cursor()

licht_value = None
temp_value = None

def on_connect(client, userdata, flags, reason_code, properties):
    print("Verbonden")
    client.subscribe("licht")
    client.subscribe("temp")

def on_message(client, userdata, msg):
    global licht_value, temp_value
    
    payload = msg.payload.decode()
    
    if msg.topic == "licht":
        licht_value = round(float(payload), 1)
        print("Licht:", licht_value)
        
    elif msg.topic == "temp":
        temp_value = round(float(payload), 1)
        print("Temp:", temp_value)

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv5
)

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)

# 🔥 Start MQTT in aparte thread
client.loop_start()

try:
    cur.execute("TRUNCATE TABLE waarde")
    conn.commit()

    while True:
        if temp_value is not None and licht_value is not None:
            cur.execute("""
                INSERT INTO waarde (time, Temp, Licht)
                VALUES (NOW(), %s, %s)
            """, (temp_value, licht_value))
            
            conn.commit()
            
        sleep(1)

except KeyboardInterrupt:
    print("Stoppen...")

finally:
    client.loop_stop()
    conn.close()
    print("Regeling gestopt")
