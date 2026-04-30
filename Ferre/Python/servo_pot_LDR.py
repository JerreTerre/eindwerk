from time import sleep, gmtime, strftime
import pymysql
from gpiozero import MCP3008, Servo
import smbus

# -------------------------
# BH1750 setup
# -------------------------
bus = smbus.SMBus(1)
BH1750_ADDR = 0x23
CMD_ONE_TIME_H_RES_MODE = 0x20

def read_bh1750():
    data = bus.read_i2c_block_data(BH1750_ADDR, CMD_ONE_TIME_H_RES_MODE, 2)
    return int((data[0] << 8 | data[1]) / 1.2)

# -------------------------
# Potmeter & Servo
# -------------------------
pot = MCP3008(channel=0)
servo = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

# -------------------------
# Database connectie
# -------------------------
conn = pymysql.connect(
    host='127.0.0.1',
    unix_socket='/var/run/mysqld/mysqld.sock',
    user='Smets',            # pas aan naar jouw gebruiker
    passwd='Thomas',         # pas aan naar jouw wachtwoord
    db='ServoDoos'
)
cur = conn.cursor()

# Optioneel: tabel leegmaken bij start
# cur.execute("TRUNCATE TABLE Doos")

try:
    while True:
        # --- Sensor uitlezen ---
        licht = read_bh1750()
        pot_value = int(pot.value * 100)

        # --- Servo hoek berekenen ---
        if pot_value <= 50:
            servo_angle = -90
        else:
            servo_angle = (pot_value - 50) * 1.8 - 90

        # --- Smooth servo beweging ---
        current_value = servo.value if servo.value is not None else 0
        target_value = max(-1, min(1, (servo_angle + 90) / 180 * 2 - 1))
        steps = 10
        for i in range(steps):
            step_value = current_value + (target_value - current_value) * (i + 1) / steps
            servo.value = max(-1, min(1, step_value))
            sleep(0.05)
        current_value = target_value

        # --- Timestamp genereren ---
        timestamp = strftime('%Y-%m-%d %H:%M:%S', gmtime())

        # --- Data loggen naar DB ---
        cur.execute(
            "INSERT INTO Doos (time, LDR, potmeter) VALUES (%s, %s, %s)",
            (timestamp, licht, pot_value)
        )
        conn.commit()

        # --- Print naar shell ---
        print(f"[{timestamp}] 💡 LDR: {licht:5d} | 🎛️ Potmeter: {pot_value:3d}% | ⚙️ Servo: {servo_angle:6.1f}°")
        sleep(1)

except KeyboardInterrupt:
    print("\nStoppen door gebruiker...")

finally:
    servo.value = None
    cur.close()
    conn.close()
