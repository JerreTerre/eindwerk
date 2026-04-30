from smbus2 import SMBus
import time

MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43

# Bewegingsdrempel (hoe gevoelig de detectie is)
GYRO_THRESHOLD = 500

def read_word(bus, reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def is_stationary(x, y, z, threshold):
    return abs(x) < threshold and abs(y) < threshold and abs(z) < threshold

with SMBus(1) as bus:
    # Sensor activeren
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

    while True:
        x = read_word(bus, GYRO_XOUT_H)
        y = read_word(bus, GYRO_XOUT_H + 2)
        z = read_word(bus, GYRO_XOUT_H + 4)

        if is_stationary(x, y, z, GYRO_THRESHOLD):
            print("Gyroscoop staat stil / recht")
        else:
            print("Gyroscoop beweegt of is scheef")

        time.sleep(0.5)