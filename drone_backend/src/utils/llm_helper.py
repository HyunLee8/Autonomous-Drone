from src.llm.gemini import get_agent_response
from src.llm.stt import transcribe_audio
import threading

# Thread synchronization
_initialization_complete = threading.Event()
tuner_lock = threading.Lock()

# Global state for LLM parameter tuning
parameter_tuner = None

current_llm_data = {
    'last_transcription': '',
    'last_response': '',
    'current_forward_threshold': 100,
    'current_backward_threshold': 125,
    'last_action': None,
    'tuner_ready': False
}


class LLMParameterTuner:
    """Helper class to tune head tracking parameters based on LLM responses"""
    
    def __init__(self, head_detector):
        """
        Initialize the LLM parameter tuner
        
        Args:
            head_detector: Instance of HeadDetector class to modify parameters
        """
        self.head_detector = head_detector
        
        # Store original values for reset functionality
        self.original_forward_threshold = head_detector.head_size_forward_threshold
        self.original_backward_threshold = head_detector.head_size_backward_threshold
        
        # Parameter constraints for safety
        self.MIN_FORWARD_THRESHOLD = 50
        self.MAX_FORWARD_THRESHOLD = 200
        self.MIN_BACKWARD_THRESHOLD = 75
        self.MAX_BACKWARD_THRESHOLD = 250
        self.MIN_THRESHOLD_GAP = 15  # Minimum gap between forward and backward thresholds
    
    def process_llm_response(self, llm_response):
        """
        Process LLM response and apply parameter changes
        
        Args:
            llm_response: Dictionary containing LLM response with actions
            
        Returns:
            Dictionary with status and applied changes
        """
        try:
            actions = llm_response.get('actions', [])
            applied_changes = []
            errors = []
            
            for action in actions:
                action_type = action.get('action', '')
                parameters = action.get('parameters', {})
                
                if action_type == 'adjust_distance_thresholds':
                    result = self._adjust_distance_thresholds(parameters)
                    if result['success']:
                        applied_changes.append(result['message'])
                    else:
                        errors.append(result['message'])
                
                elif action_type == 'move_closer':
                    result = self._move_closer()
                    if result['success']:
                        applied_changes.append(result['message'])
                    else:
                        errors.append(result['message'])
                
                elif action_type == 'move_farther':
                    result = self._move_farther()
                    if result['success']:
                        applied_changes.append(result['message'])
                    else:
                        errors.append(result['message'])
                
                elif action_type == 'reset_thresholds':
                    result = self._reset_thresholds()
                    if result['success']:
                        applied_changes.append(result['message'])
                
                elif action_type == 'get_current_settings':
                    current = self._get_current_settings()
                    applied_changes.append(current['message'])
            
            return {
                'success': len(errors) == 0,
                'applied_changes': applied_changes,
                'errors': errors,
                'current_thresholds': self._get_current_thresholds()
            }
            
        except Exception as e:
            return {
                'success': False,
                'applied_changes': [],
                'errors': [f"Error processing LLM response: {str(e)}"],
                'current_thresholds': self._get_current_thresholds()
            }
    
    def _adjust_distance_thresholds(self, parameters):
        """Adjust forward and backward thresholds"""
        try:
            # Handle absolute value setting
            if 'forward_threshold' in parameters and 'backward_threshold' in parameters:
                forward = int(parameters['forward_threshold'])
                backward = int(parameters['backward_threshold'])
                
                if not self._validate_thresholds(forward, backward):
                    return {
                        'success': False,
                        'message': f"Invalid threshold values. Must maintain minimum gap of {self.MIN_THRESHOLD_GAP}px."
                    }
                
                self.head_detector.head_size_forward_threshold = forward
                self.head_detector.head_size_backward_threshold = backward
                
                return {
                    'success': True,
                    'message': f"Thresholds updated: Forward={forward}px, Backward={backward}px"
                }
            
            # Handle relative adjustment
            elif 'adjustment' in parameters:
                adjustment = int(parameters['adjustment'])
                
                new_forward = self.head_detector.head_size_forward_threshold + adjustment
                new_backward = self.head_detector.head_size_backward_threshold + adjustment
                
                if not self._validate_thresholds(new_forward, new_backward):
                    return {
                        'success': False,
                        'message': f"Adjustment of {adjustment}px would exceed safe limits."
                    }
                
                self.head_detector.head_size_forward_threshold = new_forward
                self.head_detector.head_size_backward_threshold = new_backward
                
                direction = "farther" if adjustment > 0 else "closer"
                return {
                    'success': True,
                    'message': f"Distance adjusted {abs(adjustment)}px {direction}. New: Forward={new_forward}px, Backward={new_backward}px"
                }
            
            else:
                return {
                    'success': False,
                    'message': "Missing required parameters for threshold adjustment."
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error adjusting thresholds: {str(e)}"
            }
    
    def _move_closer(self):
        """Move the optimal tracking distance closer by 15px"""
        try:
            adjustment = -15
            new_forward = self.head_detector.head_size_forward_threshold + adjustment
            new_backward = self.head_detector.head_size_backward_threshold + adjustment
            
            if not self._validate_thresholds(new_forward, new_backward):
                return {
                    'success': False,
                    'message': "Cannot move closer - would exceed minimum threshold limits."
                }
            
            self.head_detector.head_size_forward_threshold = new_forward
            self.head_detector.head_size_backward_threshold = new_backward
            
            return {
                'success': True,
                'message': f"Moved closer by 15px. New range: {new_forward}-{new_backward}px"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error moving closer: {str(e)}"
            }
    
    def _move_farther(self):
        """Move the optimal tracking distance farther by 15px"""
        try:
            adjustment = 15
            new_forward = self.head_detector.head_size_forward_threshold + adjustment
            new_backward = self.head_detector.head_size_backward_threshold + adjustment
            
            if not self._validate_thresholds(new_forward, new_backward):
                return {
                    'success': False,
                    'message': "Cannot move farther - would exceed maximum threshold limits."
                }
            
            self.head_detector.head_size_forward_threshold = new_forward
            self.head_detector.head_size_backward_threshold = new_backward
            
            return {
                'success': True,
                'message': f"Moved farther by 15px. New range: {new_forward}-{new_backward}px"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error moving farther: {str(e)}"
            }
    
    def _reset_thresholds(self):
        """Reset thresholds to original values"""
        self.head_detector.head_size_forward_threshold = self.original_forward_threshold
        self.head_detector.head_size_backward_threshold = self.original_backward_threshold
        
        return {
            'success': True,
            'message': f"Reset to defaults: Forward={self.original_forward_threshold}px, Backward={self.original_backward_threshold}px"
        }
    
    def _get_current_settings(self):
        """Get current threshold settings"""
        forward = self.head_detector.head_size_forward_threshold
        backward = self.head_detector.head_size_backward_threshold
        optimal = (forward + backward) / 2
        
        return {
            'success': True,
            'message': f"Current: Forward={forward}px, Backward={backward}px, Optimal={optimal:.0f}px"
        }
    
    def _get_current_thresholds(self):
        """Get current threshold values as dictionary"""
        return {
            'forward_threshold': self.head_detector.head_size_forward_threshold,
            'backward_threshold': self.head_detector.head_size_backward_threshold,
            'optimal_size': (self.head_detector.head_size_forward_threshold + 
                           self.head_detector.head_size_backward_threshold) / 2
        }
    
    def _validate_thresholds(self, forward, backward):
        """Validate threshold values"""
        if forward < self.MIN_FORWARD_THRESHOLD or forward > self.MAX_FORWARD_THRESHOLD:
            return False
        
        if backward < self.MIN_BACKWARD_THRESHOLD or backward > self.MAX_BACKWARD_THRESHOLD:
            return False
        
        if backward <= forward:
            return False
        
        if (backward - forward) < self.MIN_THRESHOLD_GAP:
            return False
        
        return True
    
    def interpret_user_request(self, transcription):
        """Helper to provide context for user requests"""
        current = self._get_current_thresholds()
        
        context = f"""
Current Drone Tracking Settings:
- Forward Threshold: {current['forward_threshold']}px (drone moves forward if head is smaller)
- Backward Threshold: {current['backward_threshold']}px (drone moves backward if head is larger)
- Optimal Head Size: {current['optimal_size']:.0f}px (target distance)

User Request: {transcription}
"""
        return context


def _wait_for_tuner(timeout=10):
    """Wait for tuner to be initialized (thread-safe)"""
    if not _initialization_complete.wait(timeout=timeout):
        print(f"⚠️ Tuner initialization timed out after {timeout}s")
        return False
    return True


def initialize_tuner(head_detector):
    """Initialize the parameter tuner with head detector instance"""
    global parameter_tuner, current_llm_data, _initialization_complete
    
    print("🔧 Initializing LLM Parameter Tuner...")
    print(f"DEBUG: Current thread: {threading.current_thread().name}")
    print(f"DEBUG: parameter_tuner is None: {parameter_tuner is None}")
    
    with tuner_lock:
        print("DEBUG: Inside tuner_lock")
        # Prevent double initialization
        if parameter_tuner is not None:
            print("⚠️ Tuner already initialized, skipping...")
            _initialization_complete.set()
            return
        
        print("DEBUG: Creating LLMParameterTuner...")
        parameter_tuner = LLMParameterTuner(head_detector)
        print("DEBUG: LLMParameterTuner created")
        
        current_llm_data['tuner_ready'] = True
        current_llm_data['current_forward_threshold'] = head_detector.head_size_forward_threshold
        current_llm_data['current_backward_threshold'] = head_detector.head_size_backward_threshold
        
        # Signal that initialization is complete
        print("DEBUG: Setting _initialization_complete event")
        _initialization_complete.set()
        print("DEBUG: _initialization_complete event set")
    
def process_audio_request(audio_file):
    """Process audio file and apply LLM tuning"""
    global parameter_tuner, current_llm_data, tuner_lock
    
    try:
        print(f"Processing audio file: {audio_file.filename}")
        
        # CRITICAL FIX: Reset file pointer to beginning
        audio_file.seek(0)
        
        # Transcribe audio
        transcription = transcribe_audio(audio_file)
        
        if not transcription:
            print("No transcription received")
            return {
                'success': False,
                'error': 'Could not transcribe audio',
                'transcription': ''
            }
        
        print(f"Transcription: {transcription}")

        # Wait for tuner to be ready (up to 10 seconds)
        if not _wait_for_tuner(timeout=10):
            return {
                'success': True,
                'transcription': transcription,
                'response': f"I heard: {transcription}. System still initializing, please wait...",
                'actions_taken': [],
                'errors': ['Tuner still initializing'],
                'current_thresholds': {}
            }
        
        # Double-check if tuner is initialized
        if parameter_tuner is None:
            print("⚠️ Parameter tuner not initialized - returning transcription only")
            return {
                'success': True,
                'transcription': transcription,
                'response': f"I heard: {transcription}. But tracking system isn't initialized yet.",
                'actions_taken': [],
                'errors': ['Parameter tuner not initialized'],
                'current_thresholds': {}
            }
        
        # Process with tuner
        with tuner_lock:
            current_llm_data['last_transcription'] = transcription
            
            # Get context and LLM response
            context = parameter_tuner.interpret_user_request(transcription)
            llm_response = get_agent_response(context)
            
            current_llm_data['last_response'] = llm_response.get('response', '')
            
            # Apply parameter changes
            tuning_result = parameter_tuner.process_llm_response(llm_response)
            
            # Update current data
            thresholds = tuning_result.get('current_thresholds', {})
            current_llm_data['current_forward_threshold'] = thresholds.get('forward_threshold', 100)
            current_llm_data['current_backward_threshold'] = thresholds.get('backward_threshold', 125)
            current_llm_data['last_action'] = tuning_result.get('applied_changes', [])
            
            return {
                'success': tuning_result.get('success', False),
                'transcription': transcription,
                'response': llm_response.get('response', ''),
                'actions_taken': tuning_result.get('applied_changes', []),
                'errors': tuning_result.get('errors', []),
                'current_thresholds': thresholds
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'transcription': '',
            'response': f"Error: {str(e)}"
        }


def process_text_request(text):
    """Process text request and apply LLM tuning"""
    global parameter_tuner, current_llm_data, tuner_lock
    
    if parameter_tuner is None:
        return {
            'error': 'Parameter tuner not initialized. Start tracking first.',
            'success': False
        }
    
    with tuner_lock:
        current_llm_data['last_transcription'] = text
        
        # Get context and LLM response
        context = parameter_tuner.interpret_user_request(text)
        llm_response = get_agent_response(context)
        
        current_llm_data['last_response'] = llm_response.get('response', '')
        
        # Apply parameter changes
        tuning_result = parameter_tuner.process_llm_response(llm_response)
        
        # Update current data
        thresholds = tuning_result.get('current_thresholds', {})
        current_llm_data['current_forward_threshold'] = thresholds.get('forward_threshold', 100)
        current_llm_data['current_backward_threshold'] = thresholds.get('backward_threshold', 125)
        current_llm_data['last_action'] = tuning_result.get('applied_changes', [])
        
        return {
            'success': tuning_result.get('success', False),
            'transcription': text,
            'response': llm_response.get('response', ''),
            'actions_taken': tuning_result.get('applied_changes', []),
            'errors': tuning_result.get('errors', []),
            'current_thresholds': thresholds
        }


def reset_parameters():
    """Reset parameters to default"""
    global parameter_tuner, current_llm_data, tuner_lock
    
    if parameter_tuner is None:
        return {'error': 'Parameter tuner not initialized', 'success': False}
    
    with tuner_lock:
        result = parameter_tuner._reset_thresholds()
        
        if result['success']:
            thresholds = parameter_tuner._get_current_thresholds()
            current_llm_data['current_forward_threshold'] = thresholds['forward_threshold']
            current_llm_data['current_backward_threshold'] = thresholds['backward_threshold']
        
        return result


def get_current_thresholds():
    """Get current threshold values"""
    global parameter_tuner, tuner_lock
    
    if parameter_tuner is None:
        return None
    
    with tuner_lock:
        return parameter_tuner._get_current_thresholds()