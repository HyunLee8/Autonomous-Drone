from src.utils import drone
    
def run_flight_logic():
    global drone
    if drone is None:
        print("Drone not initialized for flight logic.")
        return