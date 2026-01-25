from djitellopy import Tello
import time

# Initialize the drone
tello = Tello()

# Connect to the drone
tello.connect()

# Get battery level (good practice before flying)
print(f"Battery: {tello.get_battery()}%")

# Takeoff
tello.takeoff()
time.sleep(2)

# Basic movements
tello.move_up(30)  # Move up 30cm
time.sleep(2)

tello.move_forward(50)  # Move forward 50cm
time.sleep(2)

tello.rotate_clockwise(90)  # Rotate 90 degrees
time.sleep(2)

# Land
tello.land()