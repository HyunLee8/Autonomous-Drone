"""
Advanced Tello Drone Controller
Handles all drone operations with advanced features like smooth tracking,
safety checks, command queuing, and PID control for stable movements.

CREDITS TO SONNET 4.5 Anthropic for PID controls
"""
from drone_backend.src.cv.head_detection import HeadDetector
from djitellopy import Tello
import time
import logging
import threading
from queue import Queue
from typing import Optional, Tuple, Callable
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIDController:
    """PID controller for smooth drone movements."""
    
    def __init__(self, kp=0.5, ki=0.0, kd=0.1):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.previous_error = 0
        self.integral = 0
        
    def calculate(self, error, dt=0.1):
        """Calculate PID output based on error."""
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.previous_error = error
        return output
    
    def reset(self):
        """Reset PID controller state."""
        self.previous_error = 0
        self.integral = 0


class TelloController:
    """Advanced controller class for DJI Tello drone operations."""
    
    def __init__(self, min_battery=20, max_height=300):
        """
        Initialize the Tello drone controller.
        
        Args:
            min_battery (int): Minimum battery level before warning (%)
            max_height (int): Maximum allowed height in cm
        """
        self.drone = None
        self.is_connected = False
        self.is_flying = False
        self.is_streaming = False
        
        # Safety settings
        self.min_battery = min_battery
        self.max_height = max_height
        self.emergency_battery = 10
        
        # Command queue for smooth operation
        self.command_queue = Queue()
        self.command_thread = None
        self.stop_thread = False
        
        # PID controllers for smooth tracking
        self.pid_x = PIDController(kp=0.4, ki=0.0, kd=0.2)
        self.pid_y = PIDController(kp=0.4, ki=0.0, kd=0.2)
        self.pid_z = PIDController(kp=0.3, ki=0.0, kd=0.15)
        
        # Tracking state
        self.tracking_enabled = False
        self.last_track_time = 0
        self.track_cooldown = 0.5  # seconds between tracking commands
        
        # State monitoring
        self.flight_stats = {
            'total_flight_time': 0,
            'commands_executed': 0,
            'start_time': None
        }
        
    def connect(self) -> bool:
        """Connect to the Tello drone with error handling."""
        try:
            self.drone = Tello()
            self.drone.connect()
            self.is_connected = True
            # Get initial status
            battery = self.drone.get_battery()
            temp = self.drone.get_temperature()
            
            logger.info(f"Connected to Tello - Battery: {battery}%, Temp: {temp}°C")
            
            # Check battery level
            if battery < self.min_battery:
                logger.warning(f"Low battery: {battery}%. Consider charging before flight.")
            
            # Start command processing thread
            self._start_command_thread()
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tello: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Safely disconnect from the Tello drone."""
        if self.is_flying:
            logger.info("Landing before disconnect...")
            self.land()
        
        if self.is_streaming:
            self.stream_off()
        
        # Stop command thread
        self.stop_thread = True
        if self.command_thread:
            self.command_thread.join(timeout=2)
        
        self.is_connected = False
        logger.info("Disconnected from Tello")
    
    def _start_command_thread(self):
        """Start background thread for processing commands."""
        self.stop_thread = False
        self.command_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.command_thread.start()
    
    def _process_commands(self):
        """Process commands from the queue in background thread."""
        while not self.stop_thread:
            try:
                if not self.command_queue.empty():
                    command_func, args = self.command_queue.get(timeout=0.1)
                    command_func(*args)
                    self.flight_stats['commands_executed'] += 1
                    time.sleep(0.1)  # Small delay between commands
                else:
                    time.sleep(0.05)
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def _check_safety(self) -> bool:
        """Check safety conditions before executing commands."""
        if not self.is_connected:
            logger.error("Drone not connected")
            return False
        
        battery = self.get_battery()
        if battery and battery < self.emergency_battery:
            logger.error(f"CRITICAL BATTERY: {battery}% - Landing immediately!")
            self.land()
            return False
        
        if battery and battery < self.min_battery:
            logger.warning(f"Low battery: {battery}%")
        
        height = self.get_height()
        if height and height > self.max_height:
            logger.warning(f"Height {height}cm exceeds max {self.max_height}cm")
            return False
        
        return True
    
    def takeoff(self) -> bool:
        """Take off the drone with safety checks."""
        if not self._check_safety():
            return False
        
        try:
            self.drone.takeoff()
            self.drone.move_up(80)
            self.is_flying = True
            self.flight_stats['start_time'] = time.time()
            logger.info("Drone took off")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Takeoff failed: {e}")
            return False
    
    def land(self) -> bool:
        """Land the drone and update stats."""
        if not self.is_connected:
            return False
        
        try:
            self.drone.land()
            self.is_flying = False
            
            if self.flight_stats['start_time']:
                flight_time = time.time() - self.flight_stats['start_time']
                self.flight_stats['total_flight_time'] += flight_time
                logger.info(f"Drone landed. Flight time: {flight_time:.1f}s")
            
            return True
        except Exception as e:
            logger.error(f"Landing failed: {e}")
            return False
    
    def _execute_movement(self, command_func: Callable, distance: int, direction: str) -> bool:
        """
        Execute movement with safety checks.
        
        Args:
            command_func: The drone command function to execute
            distance: Distance to move (cm)
            direction: Direction name for logging
        """
        if not self.is_flying or not self._check_safety():
            return False
        
        try:
            # Clamp distance to safe range
            distance = max(20, min(500, distance))
            command_func(distance)
            logger.info(f"Moved {direction} {distance}cm")
            return True
        except Exception as e:
            logger.error(f"Move {direction} failed: {e}")
            return False
    
    def move_up(self, distance: int) -> bool:
        """Move drone up with safety checks."""
        return self._execute_movement(self.drone.move_up, distance, "up")
    
    def move_down(self, distance: int) -> bool:
        """Move drone down with safety checks."""
        return self._execute_movement(self.drone.move_down, distance, "down")
    
    def move_left(self, distance: int) -> bool:
        """Move drone left with safety checks."""
        return self._execute_movement(self.drone.move_left, distance, "left")
    
    def move_right(self, distance: int) -> bool:
        """Move drone right with safety checks."""
        return self._execute_movement(self.drone.move_right, distance, "right")
    
    def move_forward(self, distance: int) -> bool:
        """Move drone forward with safety checks."""
        return self._execute_movement(self.drone.move_forward, distance, "forward")
    
    def move_back(self, distance: int) -> bool:
        """Move drone back with safety checks."""
        return self._execute_movement(self.drone.move_back, distance, "back")
    
    def rotate_clockwise(self, degrees: int) -> bool:
        """Rotate drone clockwise."""
        if not self.is_flying or not self._check_safety():
            return False
        
        try:
            degrees = max(1, min(360, degrees))
            self.drone.rotate_clockwise(degrees)
            logger.info(f"Rotated clockwise {degrees}°")
            return True
        except Exception as e:
            logger.error(f"Rotate failed: {e}")
            return False
    
    def rotate_counter_clockwise(self, degrees: int) -> bool:
        """Rotate drone counter-clockwise."""
        if not self.is_flying or not self._check_safety():
            return False
        
        try:
            degrees = max(1, min(360, degrees))
            self.drone.rotate_counter_clockwise(degrees)
            logger.info(f"Rotated counter-clockwise {degrees}°")
            return True
        except Exception as e:
            logger.error(f"Rotate failed: {e}")
            return False
    
    def track_target(self, target_x: float, target_y: float, target_z: float = None,
                    frame_center_x: float = 0.5, frame_center_y: float = 0.5) -> bool:
        """
        Track a target using PID control for smooth movements.
        
        Args:
            target_x: Target x position (0-1, normalized to frame)
            target_y: Target y position (0-1, normalized to frame)
            target_z: Optional target size for depth control (0-1)
            frame_center_x: Center x of frame (default 0.5)
            frame_center_y: Center y of frame (default 0.5)
        
        Returns:
            bool: True if commands were sent
        """
        if not self.is_flying or not self._check_safety():
            return False
        
        # Cooldown check to prevent command spam
        current_time = time.time()
        if current_time - self.last_track_time < self.track_cooldown:
            return False
        
        self.last_track_time = current_time
        
        # Calculate errors (distance from center)
        error_x = target_x - frame_center_x
        error_y = frame_center_y - target_y  # Inverted for drone coordinates
        
        # PID control
        control_x = self.pid_x.calculate(error_x)
        control_y = self.pid_y.calculate(error_y)
        
        # Dead zone to prevent jitter
        dead_zone = 0.1
        if abs(error_x) < dead_zone and abs(error_y) < dead_zone:
            return False
        
        # Convert to drone commands
        # Scale control output to reasonable movement distances (20-50cm)
        move_distance_x = int(np.clip(abs(control_x) * 100, 20, 50))
        move_distance_y = int(np.clip(abs(control_y) * 100, 20, 50))
        
        # Execute movements
        if abs(error_x) > dead_zone:
            if control_x > 0:
                self.move_right(move_distance_x)
            else:
                self.move_left(move_distance_x)
        
        if abs(error_y) > dead_zone:
            if control_y > 0:
                self.move_up(move_distance_y)
            else:
                self.move_down(move_distance_y)
        
        # Optional depth control based on target size
        if target_z is not None:
            error_z = target_z - 0.3  # Target size around 30% of frame
            if abs(error_z) > 0.1:
                control_z = self.pid_z.calculate(error_z)
                move_distance_z = int(np.clip(abs(control_z) * 80, 20, 50))
                
                if control_z < 0:  # Target too small, move forward
                    self.move_forward(move_distance_z)
                else:  # Target too large, move back
                    self.move_back(move_distance_z)
        
        return True
    
    def flip(self, direction: str) -> bool:
        """
        Perform a flip in the specified direction.
        
        Args:
            direction: 'l' (left), 'r' (right), 'f' (forward), 'b' (back)
        """
        if not self.is_flying or not self._check_safety():
            return False
        
        try:
            self.drone.flip(direction)
            logger.info(f"Performed flip: {direction}")
            return True
        except Exception as e:
            logger.error(f"Flip failed: {e}")
            return False
    
    def send_rc_control(self, left_right: int, forward_backward: int, 
                       up_down: int, yaw: int) -> bool:
        """
        Send RC control commands for continuous movement.
        
        Args:
            left_right: -100 to 100 (left/right)
            forward_backward: -100 to 100 (forward/backward)
            up_down: -100 to 100 (up/down)
            yaw: -100 to 100 (rotation)
        """
        if not self.is_flying or not self._check_safety():
            return False
        
        try:
            self.drone.send_rc_control(left_right, forward_backward, up_down, yaw)
            return True
        except Exception as e:
            logger.error(f"RC control failed: {e}")
            return False
    
    def hover(self):
        """Stop all movement and hover in place."""
        return self.send_rc_control(0, 0, 0, 0)
    
    def get_battery(self) -> Optional[int]:
        """Get current battery level."""
        if not self.is_connected:
            return None
        try:
            return self.drone.get_battery()
        except Exception as e:
            logger.error(f"Failed to get battery: {e}")
            return None
    
    def get_height(self) -> Optional[int]:
        """Get current height in cm."""
        if not self.is_connected:
            return None
        try:
            return self.drone.get_height()
        except Exception as e:
            logger.error(f"Failed to get height: {e}")
            return None
    
    def get_temperature(self) -> Optional[int]:
        """Get current temperature in °C."""
        if not self.is_connected:
            return None
        try:
            return self.drone.get_temperature()
        except Exception as e:
            logger.error(f"Failed to get temperature: {e}")
            return None
    
    def get_flight_time(self) -> Optional[int]:
        """Get current flight time in seconds."""
        if not self.is_connected:
            return None
        try:
            return self.drone.get_flight_time()
        except Exception as e:
            logger.error(f"Failed to get flight time: {e}")
            return None
    
    def get_status(self) -> dict:
        """Get comprehensive drone status."""
        status = {
            'connected': self.is_connected,
            'flying': self.is_flying,
            'streaming': self.is_streaming,
            'battery': self.get_battery(),
            'height': self.get_height(),
            'temperature': self.get_temperature(),
            'flight_time': self.get_flight_time(),
            'total_commands': self.flight_stats['commands_executed']
        }
        return status
    
    def emergency_stop(self):
        """Emergency stop - cuts motors immediately. USE WITH CAUTION!"""
        if self.drone:
            try:
                self.drone.emergency()
                self.is_flying = False
                logger.warning("EMERGENCY STOP ACTIVATED - MOTORS CUT")
            except Exception as e:
                logger.error(f"Emergency stop failed: {e}")

    def emergency_land(self):
      """Emergency landing - faster descent than normal land."""
      if not self.is_flying:
          return False
      
      logger.warning("EMERGENCY LANDING - RAPID DESCENT")
      
      try:
          # Hover to stop lateral movement
          self.send_rc_control(0, 0, 0, 0)
          time.sleep(0.2)
          
          # Quick descent
          for _ in range(15):
              self.send_rc_control(0, 0, -80, 0)  # Fast down
              time.sleep(0.1)
          
          # Final normal land
          self.land()
          return True

      except Exception as e:
        logger.error(f"Emergency land failed, using emergency_stop: {e}")
        self.emergency_stop()  # Last resort
        return False

    def stream_on(self) -> bool:
        """Turn on video stream."""
        if not self.is_connected:
            return False
        try:
            self.drone.streamon()
            self.is_streaming = True
            logger.info("Video stream started")
            return True
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")
            return False
    
    def stream_off(self) -> bool:
        """Turn off video stream."""
        if not self.is_connected:
            return False
        try:
            self.drone.streamoff()
            self.is_streaming = False
            logger.info("Video stream stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop stream: {e}")
            return False
    
    def get_frame(self):
        """Get current video frame from drone camera."""
        if not self.is_connected or not self.is_streaming:
            return None
        try:
            return self.drone.get_frame_read().frame
        except Exception as e:
            logger.error(f"Failed to get frame: {e}")
            return None

    def wait_for_stream(self, timeout=10) -> bool:
        """Wait for video stream to be ready with frames."""
        if not self.is_streaming:
            logger.warning("Stream not started")
            return False
        
        logger.info("Waiting for video stream to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            frame = self.get_frame()
            if frame is not None:
                logger.info("Video stream ready!")
                return True
            time.sleep(0.1)
        
        logger.error("Video stream failed to start within timeout")
        return False
    
    def reset_tracking(self):
        """Reset PID controllers for tracking."""
        self.pid_x.reset()
        self.pid_y.reset()
        self.pid_z.reset()
        logger.info("Tracking controllers reset")


# Example usage and testing
if __name__ == "__main__":
    controller = TelloController(min_battery=30, max_height=250)
    
    if controller.connect():
        status = controller.get_status()
        print(f"Drone Status: {status}")
        
        # Uncomment to test advanced features
        # controller.takeoff()
        # time.sleep(2)
        
        # Test smooth tracking (simulated target at 60% x, 40% y)
        # controller.track_target(0.6, 0.4)
        # time.sleep(1)
        
        # controller.land()
        controller.disconnect()