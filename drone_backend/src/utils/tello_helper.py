from src.tello import FlightLogic, TelloController, get_head_detector  # Add get_head_detector
from src.utils.llm_helper import initialize_tuner

Flight_logic_instance = None

def run_logic():
    global Flight_logic_instance
    Flight_logic_instance = FlightLogic()
    Flight_logic_instance.start_flight_sequence()
    
def stop_logic():
    global Flight_logic_instance
    if Flight_logic_instance and Flight_logic_instance.drone:
        Flight_logic_instance.drone.land()
    else:
        print("No active drone to stop.")