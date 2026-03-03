import time
import random

# Tank settings
TANK_CAPACITY = 100
water_level = 10   # starting level
motor_on = False

def display_status():
    print("\n--------------------------")
    print(f"Water Level: {water_level}%")
    print(f"Motor Status: {'ON' if motor_on else 'OFF'}")
    print("--------------------------")

while True:
    # Motor control logic
    if water_level <= 20:
        motor_on = True
        print("⚡ Water low! Motor turned ON")

    if water_level >= 95:
        motor_on = False
        print("🚨 Tank almost full! Motor turned OFF")

    # Simulate filling
    if motor_on:
        water_level += random.randint(1, 3)
    else:
        water_level -= random.randint(0, 2)  # usage simulation

    # Prevent overflow / underflow
    water_level = max(0, min(TANK_CAPACITY, water_level))

    display_status()

    time.sleep(2)
