import paho.mqtt.client as mqtt

# MQTT instellingen
broker = "localhost"
port = 1883
topic1 = "temp"
topic2= "licht"

# Callback bij verbinden (API v5)
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Verbonden met MQTT broker")
        client.subscribe(topic1)
        print(f"Geabonneerd op topic: {topic1}")
    else:
        print("Verbinding mislukt, code:", reason_code)

# Callback bij ontvangen bericht
def on_message(client, userdata, msg):
    print(f"Ontvangen op {msg.topic}: {msg.payload.decode()}")

# Client aanmaken met nieuwe API
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Verbinden
client.connect(broker, port, 60)

# Blijft luisteren
client.loop_forever()