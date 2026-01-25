from djitellopy import Tello
import time

tello = Tello()

tello.connect()

print(f"Battery: {tello.get_battery()}%")

tello.takeoff()
time.sleep(2)

tello.move_up(30)  # Move up 30cm
time.sleep(2)

tello.move_forward(50)  # Move forward 50cm
time.sleep(2)

tello.rotate_clockwise(90)  # Rotate 90 degrees
time.sleep(2)

tello.land()