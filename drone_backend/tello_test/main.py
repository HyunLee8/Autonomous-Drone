from djitellopy import Tello
import time

tello = Tello()

tello.connect()

battery = tello.get_battery()
print(f"Battery: {battery}%")

if battery < 10:
    print("Battery too low! Please charge the drone before flying.")
    exit()

print("Taking off...")
tello.takeoff()

print("Hovering for 3 sec")
time.sleep(3)

print("Landing...")
tello.land()

print("Done!")