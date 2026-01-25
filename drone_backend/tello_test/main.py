from djitellopy import Tello
import time

# Initialize the drone
tello = Tello()

# Connect to the drone
tello.connect()

# Get battery level
battery = tello.get_battery()
print(f"Battery: {battery}%")

# Check if battery is sufficient
if battery < 10:
    print("Battery too low! Please charge the drone before flying.")
    exit()

# Takeoff
print("Taking off...")
tello.takeoff()

# Hold for 3 seconds
print("Hovering for 3 seconds...")
time.sleep(3)

# Land
print("Landing...")
tello.land()

print("Done!")