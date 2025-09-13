"""
🤖 Motion Controller

Handles robot movement and physical actions.
Interfaces with motor controllers and servo systems for humanoid movement.
"""

import time
import threading
from typing import Dict, List, Optional, Tuple
from enum import Enum

class MovementType(Enum):
    """Types of robot movements."""
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"
    WAVE_HAND = "wave_hand"
    NOD_HEAD = "nod_head"
    SHAKE_HEAD = "shake_head"

class MotionController:
    """
    🤖 Motion Controller
    
    Handles robot movement and physical actions including:
    - Wheel-based movement
    - Servo-controlled gestures
    - Head movements
    - Hand gestures
    """
    
    def __init__(self):
        """Initialize motion controller."""
        # Motor settings
        self.motor_speed = 50  # 0-100
        self.turn_speed = 30   # 0-100
        self.movement_duration = 1.0  # seconds
        
        # Servo settings
        self.servo_positions = {
            'head_pan': 90,      # 0-180 degrees
            'head_tilt': 90,     # 0-180 degrees
            'left_hand': 90,     # 0-180 degrees
            'right_hand': 90,    # 0-180 degrees
            'left_arm': 90,      # 0-180 degrees
            'right_arm': 90      # 0-180 degrees
        }
        
        # Movement state
        self.is_moving = False
        self.current_movement = None
        self.movement_thread = None
        
        # Safety settings
        self.emergency_stop = False
        self.max_movement_time = 10.0  # seconds
        
        print("✅ Motion controller initialized")
    
    def move_forward(self, duration: float = None, speed: int = None) -> bool:
        """
        Move robot forward.
        
        Args:
            duration: Movement duration in seconds
            speed: Movement speed (0-100)
            
        Returns:
            True if movement started successfully
        """
        return self._execute_movement(MovementType.FORWARD, duration, speed)
    
    def move_backward(self, duration: float = None, speed: int = None) -> bool:
        """
        Move robot backward.
        
        Args:
            duration: Movement duration in seconds
            speed: Movement speed (0-100)
            
        Returns:
            True if movement started successfully
        """
        return self._execute_movement(MovementType.BACKWARD, duration, speed)
    
    def turn_left(self, duration: float = None, speed: int = None) -> bool:
        """
        Turn robot left.
        
        Args:
            duration: Turn duration in seconds
            speed: Turn speed (0-100)
            
        Returns:
            True if movement started successfully
        """
        return self._execute_movement(MovementType.TURN_LEFT, duration, speed)
    
    def turn_right(self, duration: float = None, speed: int = None) -> bool:
        """
        Turn robot right.
        
        Args:
            duration: Turn duration in seconds
            speed: Turn speed (0-100)
            
        Returns:
            True if movement started successfully
        """
        return self._execute_movement(MovementType.TURN_RIGHT, duration, speed)
    
    def stop(self) -> bool:
        """
        Stop all robot movement.
        
        Returns:
            True if stop command executed
        """
        try:
            self.emergency_stop = True
            self.is_moving = False
            
            if self.movement_thread:
                self.movement_thread.join(timeout=1.0)
            
            # Execute stop command
            self._send_motor_command('stop')
            
            print("⏹️ Robot stopped")
            return True
            
        except Exception as e:
            print(f"❌ Stop command error: {e}")
            return False
    
    def wave_hand(self, hand: str = 'right') -> bool:
        """
        Wave robot's hand.
        
        Args:
            hand: Which hand to wave ('left' or 'right')
            
        Returns:
            True if gesture started successfully
        """
        try:
            if hand not in ['left', 'right']:
                print("❌ Invalid hand specified")
                return False
            
            print(f"👋 Waving {hand} hand...")
            
            # Execute wave gesture
            self._execute_servo_gesture(f'{hand}_hand', 'wave')
            
            return True
            
        except Exception as e:
            print(f"❌ Wave hand error: {e}")
            return False
    
    def nod_head(self, times: int = 1) -> bool:
        """
        Nod robot's head.
        
        Args:
            times: Number of nods
            
        Returns:
            True if gesture started successfully
        """
        try:
            print(f"👤 Nodding head {times} time(s)...")
            
            # Execute nod gesture
            self._execute_servo_gesture('head_tilt', 'nod', times)
            
            return True
            
        except Exception as e:
            print(f"❌ Nod head error: {e}")
            return False
    
    def shake_head(self, times: int = 1) -> bool:
        """
        Shake robot's head.
        
        Args:
            times: Number of shakes
            
        Returns:
            True if gesture started successfully
        """
        try:
            print(f"👤 Shaking head {times} time(s)...")
            
            # Execute shake gesture
            self._execute_servo_gesture('head_pan', 'shake', times)
            
            return True
            
        except Exception as e:
            print(f"❌ Shake head error: {e}")
            return False
    
    def _execute_movement(self, movement_type: MovementType, 
                         duration: float = None, speed: int = None) -> bool:
        """
        Execute robot movement.
        
        Args:
            movement_type: Type of movement
            duration: Movement duration
            speed: Movement speed
            
        Returns:
            True if movement started successfully
        """
        try:
            if self.is_moving:
                print("⚠️ Robot is already moving")
                return False
            
            if self.emergency_stop:
                print("⚠️ Emergency stop is active")
                return False
            
            duration = duration or self.movement_duration
            speed = speed or self.motor_speed
            
            # Validate parameters
            duration = max(0.1, min(duration, self.max_movement_time))
            speed = max(1, min(speed, 100))
            
            self.is_moving = True
            self.current_movement = movement_type
            
            # Start movement in separate thread
            self.movement_thread = threading.Thread(
                target=self._movement_worker,
                args=(movement_type, duration, speed),
                daemon=True
            )
            self.movement_thread.start()
            
            print(f"🤖 {movement_type.value} movement started")
            return True
            
        except Exception as e:
            print(f"❌ Movement execution error: {e}")
            self.is_moving = False
            return False
    
    def _movement_worker(self, movement_type: MovementType, duration: float, speed: int):
        """Worker thread for robot movement."""
        try:
            start_time = time.time()
            
            # Send motor command
            self._send_motor_command(movement_type.value, speed)
            
            # Wait for movement duration
            while time.time() - start_time < duration:
                if self.emergency_stop:
                    break
                time.sleep(0.1)
            
            # Stop movement
            self._send_motor_command('stop')
            
        except Exception as e:
            print(f"❌ Movement worker error: {e}")
        finally:
            self.is_moving = False
            self.current_movement = None
    
    def _send_motor_command(self, command: str, speed: int = None):
        """
        Send command to motor controller.
        
        Args:
            command: Motor command
            speed: Motor speed (0-100)
        """
        try:
            # This would interface with actual motor controller
            # For now, simulate the command
            
            if command == 'forward':
                print(f"🔄 Moving forward at speed {speed}")
            elif command == 'backward':
                print(f"🔄 Moving backward at speed {speed}")
            elif command == 'turn_left':
                print(f"🔄 Turning left at speed {speed}")
            elif command == 'turn_right':
                print(f"🔄 Turning right at speed {speed}")
            elif command == 'stop':
                print("🛑 Stopping motors")
            
            # Simulate command processing time
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Motor command error: {e}")
    
    def _execute_servo_gesture(self, servo: str, gesture: str, times: int = 1):
        """
        Execute servo gesture.
        
        Args:
            servo: Servo name
            gesture: Gesture type
            times: Number of repetitions
        """
        try:
            for i in range(times):
                if self.emergency_stop:
                    break
                
                if gesture == 'wave':
                    # Wave gesture sequence
                    self._set_servo_position(servo, 45)   # Start position
                    time.sleep(0.3)
                    self._set_servo_position(servo, 135)  # Wave position
                    time.sleep(0.3)
                    self._set_servo_position(servo, 45)   # Back to start
                    time.sleep(0.3)
                    self._set_servo_position(servo, 90)   # Rest position
                
                elif gesture == 'nod':
                    # Nod gesture sequence
                    self._set_servo_position(servo, 60)   # Nod down
                    time.sleep(0.2)
                    self._set_servo_position(servo, 120)  # Nod up
                    time.sleep(0.2)
                    self._set_servo_position(servo, 90)   # Rest position
                
                elif gesture == 'shake':
                    # Shake gesture sequence
                    self._set_servo_position(servo, 60)   # Shake left
                    time.sleep(0.2)
                    self._set_servo_position(servo, 120)  # Shake right
                    time.sleep(0.2)
                    self._set_servo_position(servo, 90)   # Rest position
                
                if i < times - 1:  # Don't wait after last repetition
                    time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Servo gesture error: {e}")
    
    def _set_servo_position(self, servo: str, position: int):
        """
        Set servo position.
        
        Args:
            servo: Servo name
            position: Position (0-180 degrees)
        """
        try:
            # Validate position
            position = max(0, min(180, position))
            
            # Update internal position
            if servo in self.servo_positions:
                self.servo_positions[servo] = position
            
            # This would send actual servo command
            print(f"🎛️ {servo} servo set to {position}°")
            
            # Simulate servo movement time
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Servo position error: {e}")
    
    def set_motor_speed(self, speed: int):
        """
        Set default motor speed.
        
        Args:
            speed: Motor speed (0-100)
        """
        self.motor_speed = max(1, min(100, speed))
        print(f"✅ Motor speed set to {self.motor_speed}")
    
    def set_turn_speed(self, speed: int):
        """
        Set default turn speed.
        
        Args:
            speed: Turn speed (0-100)
        """
        self.turn_speed = max(1, min(100, speed))
        print(f"✅ Turn speed set to {self.turn_speed}")
    
    def set_movement_duration(self, duration: float):
        """
        Set default movement duration.
        
        Args:
            duration: Duration in seconds
        """
        self.movement_duration = max(0.1, min(10.0, duration))
        print(f"✅ Movement duration set to {self.movement_duration}s")
    
    def get_motion_status(self) -> Dict[str, Any]:
        """Get current motion status."""
        return {
            'is_moving': self.is_moving,
            'current_movement': self.current_movement.value if self.current_movement else None,
            'emergency_stop': self.emergency_stop,
            'motor_speed': self.motor_speed,
            'turn_speed': self.turn_speed,
            'movement_duration': self.movement_duration,
            'servo_positions': self.servo_positions.copy()
        }
    
    def test_motion_system(self) -> bool:
        """
        Test motion system functionality.
        
        Returns:
            True if test successful
        """
        try:
            print("🧪 Testing motion system...")
            
            # Test servo movements
            print("Testing servo movements...")
            self.wave_hand('right')
            time.sleep(1)
            self.nod_head(2)
            time.sleep(1)
            self.shake_head(2)
            time.sleep(1)
            
            # Test motor movements (simulated)
            print("Testing motor movements...")
            self.move_forward(0.5, 30)
            time.sleep(1)
            self.turn_left(0.5, 20)
            time.sleep(1)
            self.turn_right(0.5, 20)
            time.sleep(1)
            self.move_backward(0.5, 30)
            time.sleep(1)
            
            print("✅ Motion system test successful")
            return True
            
        except Exception as e:
            print(f"❌ Motion system test error: {e}")
            return False
    
    def emergency_stop_all(self):
        """Emergency stop all robot movements."""
        try:
            self.emergency_stop = True
            self.stop()
            
            # Reset all servos to rest position
            for servo in self.servo_positions:
                self._set_servo_position(servo, 90)
            
            print("🚨 Emergency stop activated")
            
        except Exception as e:
            print(f"❌ Emergency stop error: {e}")
    
    def reset_emergency_stop(self):
        """Reset emergency stop status."""
        self.emergency_stop = False
        print("✅ Emergency stop reset")
    
    def cleanup(self):
        """Clean up motion controller resources."""
        try:
            self.stop()
            self.emergency_stop_all()
            print("🧹 Motion controller cleaned up")
        except Exception as e:
            print(f"❌ Motion controller cleanup error: {e}")