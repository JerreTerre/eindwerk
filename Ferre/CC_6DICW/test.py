from gpiozero import AngularServo
from time import sleep
from simple_pid import PID
from threading import Lock
import _thread
from flask import Flask, request, render_template
import busio
import board
import adafruit_bh1750
import pymysql
import paho.mqtt.client as mqtt

# =========================
# HARDWARE
# =========================


i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bh1750.BH1750(i2c)
servo = AngularServo(17, initial_angle=0, min_angle=180, max_angle=0, min_pulse_width=7/10000, max_pulse_width=25/10000)
servo.angle=60
# =========================
# VARIABELEN & PID
# =========================
lichtX = 0.0  # Gemeten temperatuur
W = 400     # Setpoint (Gewenste temp)
y = 0.0      # Stuurwaarde in %



kalmin= None
kalmax=None


conn = pymysql.connect(
    host='127.0.0.1',
    unix_socket='/var/run/mysqld/mysqld.sock',
    user='Smets',
    passwd='Thomas',
    db='paasexaam'
)
cur = conn.cursor()
try:

        cur.execute("TRUNCATE TABLE waarden")
        conn.commit()
        while True:
            # 1. Meten
            lichtX=round(sensor.lux)
            print(lichtX)
            val = max(0, min(100, y))
            print(val)
            servo.angle = val
            cur.execute("""
                INSERT INTO waarden (time, W, X, Y)
                VALUES (NOW(), %s, %s, %s)
            """, (W, lichtX, y))
            conn.commit()

finally:
        servo.angle=60



