from gpiozero import Button
import spidev
from time import sleep, gmtime, strftime
import io 
import pymysql
import os
# Open database connection (IP, mysql naam, mysql paswoord, databasenaam)
conn = pymysql.connect(host='127.0.0.1', unix_socket='/var/run/mysqld/mysqld.sock', user='Smets', passwd='Thomas', db='CC1')
cur = conn.cursor()
kal_klein = 0
kal_groot = 0
teller_klein = 0
teller_groot = 0

# --- GPIO setup ---
kbutton = Button(21, pull_up=True, bounce_time=0.1)  
gbutton = Button(20, pull_up=True, bounce_time=0.1)

# --- SPI setup ---
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000

# --- Functies ---
def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    return value

def read_voltage(channel):
    value = read_adc(channel)
    return (value * 3.3) / 1023.0

def voltage_to_distance(v):
    if v <= 0.2:
        return 80
    dist = 24 / v
    return max(10, min(80, dist))

def kalklein():
    global kal_klein
    v = read_voltage(0)
    kal_klein = voltage_to_distance(v)
    print(f"Klein blokje gekalibreerd op {kal_klein:.1f} cm")
    sleep(0.2)

def kalgroot():
    global kal_groot
    v = read_voltage(0)
    kal_groot = voltage_to_distance(v)
    print(f"Groot blokje gekalibreerd op {kal_groot:.1f} cm")
    sleep(0.2)

# --- Events ---
kbutton.when_pressed = kalklein
gbutton.when_pressed = kalgroot

# --- Hoofdlus ---
try:
    cur.execute("TRUNCATE TABLE Blok")
    while True:
        os.system("clear")
        voltage = read_voltage(0)
        distance = voltage_to_distance(voltage)

        print(f"📏 Afstand: {distance:5.1f} cm | 🔋 {voltage:4.2f} V")
        print(f"Klein teller: {teller_klein} | Groot teller: {teller_groot}")
        print(f"(Druk K voor klein, G voor groot kalibratie)")

        # Vergelijken met tolerantie
        if distance<(kal_klein*1.02)and distance>(kal_klein*0.98):
            teller_klein += 1
            print("🟢 Klein blokje gedetecteerd!")

        elif distance<(kal_groot*1.02)and distance>(kal_groot*0.98):
            teller_groot += 1
            print("🔵 Groot blokje gedetecteerd!")

        cur.execute("INSERT INTO Blok(time,blokK,blokG) VALUES (%s,%s,%s)",(strftime('%Y-%m-%d %H:%M:%S',gmtime()),teller_klein,teller_groot))
        conn.commit()
        sleep(0.5)

except KeyboardInterrupt:
    spi.close()
    print("\nProgramma gestopt.")