from time import sleep
import paho.mqtt.client as mqtt
import board
import busio
import adafruit_bmp280
import os
import json

i2c = busio.I2C(board.SCL, board.SDA)
bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

broker = "localhost"
port = 1883
topic = "temp"

# Callback bij verbinden
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Verbonden met MQTT broker")
    else:
        print("Verbinding mislukt:", reason_code)

# MQTT client (nieuwe API)
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv5
)

client.username_pw_set("Ferre", "Terryn")
client.on_connect = on_connect
client.connect(broker, port, keepalive=60)

client.loop_start()

try:
    while True:
        
        temp = bmp.temperature
        
        payload = json.dumps({
            "temperature": round(temp, 2)
        })
        
        client.publish(topic, payload)
        print(f"Verzonden: {temp} °C")
        sleep(1)

except KeyboardInterrupt:
    print("Stoppen...")
    client.loop_stop()
    client.disconnect()