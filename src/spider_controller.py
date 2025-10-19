"""
Spider Controller - Enhanced Quadruped Movement System
Supports 12-servo spider robot with realistic movements
"""

import time
import math
from typing import Optional, List, Tuple
from dataclasses import dataclass

try:
    from adafruit_servokit import ServoKit
    SERVO_AVAILABLE = True
except ImportError:
    print("Warning: ServoKit not available - using mock servo control")
    SERVO_AVAILABLE = False

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    print("Warning: RPi.GPIO not available - using mock GPIO")
    GPIO_AVAILABLE = False

from config.hardware_config import SERVO_PINS, ULTRASONIC_PINS
from src.oled_display import OLEDDisplay


@dataclass
class ServoPosition:
    """Servo position configuration"""
    shoulder: int = 90
    elbow: int = 90
    foot: int = 90


class SpiderController:
    """Main spider robot controller with realistic movements"""
    
    def __init__(self, oled_display: Optional[OLEDDisplay] = None):
        self.oled = oled_display
        self.servos = None
        self.is_moving = False
        self.current_mode = "IDLE"
        
        # Movement parameters
        self.step_height = 30  # degrees
        self.step_forward = 20  # degrees
        self.turn_angle = 15  # degrees
        self.movement_speed = 0.02  # seconds between servo updates
        
        # Servo limits (safety)
        self.servo_min = 0
        self.servo_max = 180
        
        # Home positions for all legs
        self.home_positions = {
            'leg1': ServoPosition(90, 120, 60),  # Front Right
            'leg2': ServoPosition(90, 120, 60),  # Front Left
            'leg3': ServoPosition(90, 60, 120),  # Back Right
            'leg4': ServoPosition(90, 60, 120),  # Back Left
        }
        
        # Current positions
        self.current_positions = {
            leg: ServoPosition(pos.shoulder, pos.elbow, pos.foot)
            for leg, pos in self.home_positions.items()
        }
        
        # Initialize hardware
        self._initialize_hardware()
        
    def _initialize_hardware(self):
        """Initialize servo controller and sensors"""
        print("Initializing spider hardware...")
        
        # Initialize servo controller
        if SERVO_AVAILABLE:
            try:
                self.servos = ServoKit(channels=16)
                print("   PCA9685 servo controller initialized")
                
                # Set servo ranges
                for i in range(12):
                    self.servos.servo[i].actuation_range = 180
                    
                # Move to home position
                self.go_home()
                print("   Servos moved to home position")
                
            except Exception as e:
                print(f"   Error: Servo initialization failed: {e}")
                self.servos = None
        else:
            print("   Using mock servo control")
            
        # Initialize GPIO for ultrasonic sensor
        if GPIO_AVAILABLE:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(ULTRASONIC_PINS['trigger'], GPIO.OUT)
                GPIO.setup(ULTRASONIC_PINS['echo'], GPIO.IN)
                print("   Ultrasonic sensor initialized")
            except Exception as e:
                print(f"   Error: GPIO initialization failed: {e}")
        else:
            print("   Using mock ultrasonic sensor")
            
    def _set_servo(self, leg: str, joint: str, angle: int):
        """Set individual servo position with safety limits"""
        # Clamp angle to safe range
        angle = max(self.servo_min, min(self.servo_max, angle))
        
        # Get servo index
        servo_key = f"{leg}_{joint}"
        if servo_key not in SERVO_PINS:
            return
            
        servo_index = SERVO_PINS[servo_key]
        
        # Update current position
        if leg in self.current_positions:
            setattr(self.current_positions[leg], joint, angle)
        
        # Move servo
        if self.servos:
            try:
                self.servos.servo[servo_index].angle = angle
            except Exception as e:
                print(f"Servo error ({servo_key}): {e}")
            
    def _set_leg_position(self, leg: str, shoulder: int, elbow: int, foot: int):
        """Set all joints of a leg"""
        self._set_servo(leg, 'shoulder', shoulder)
        time.sleep(0.01)
        self._set_servo(leg, 'elbow', elbow)
        time.sleep(0.01)
        self._set_servo(leg, 'foot', foot)
        
    def go_home(self):
        """Move all legs to home position"""
        print("Moving to home position...")
        self.current_mode = "HOME"
        
        for leg, position in self.home_positions.items():
            self._set_leg_position(leg, position.shoulder, 
                                  position.elbow, position.foot)
            time.sleep(0.1)
            
        if self.oled:
            self.oled.update_mode("HOME")
            
    def stand_up(self):
        """Stand up from sitting position"""
        print("Standing up...")
        self.current_mode = "STANDING"
        
        # Gradually raise body
        for i in range(10):
            progress = i / 10
            for leg in self.home_positions.keys():
                home = self.home_positions[leg]
                self._set_servo(leg, 'elbow', 
                              int(home.elbow + (1 - progress) * 30))
            time.sleep(0.05)
            
        self.go_home()
        
        if self.oled:
            self.oled.update_mode("READY")
            
    def sit_down(self):
        """Sit down by lowering body"""
        print("Sitting down...")
        self.current_mode = "SITTING"
        
        # Gradually lower body
        for i in range(10):
            progress = i / 10
            for leg in self.home_positions.keys():
                home = self.home_positions[leg]
                self._set_servo(leg, 'elbow', 
                              int(home.elbow + progress * 30))
            time.sleep(0.05)
            
        if self.oled:
            self.oled.update_mode("SITTING")
            
    def walk_forward(self, steps: int = 3):
        """Walk forward with alternating tripod gait"""
        print(f"Walking forward ({steps} steps)...")
        self.is_moving = True
        self.current_mode = "WALKING"
        
        if self.oled:
            self.oled.update_mode("WALKING")
        
        try:
            for step in range(steps):
                # Phase 1: Lift legs 1, 3, 4 (diagonal tripod)
                self._lift_legs(['leg1', 'leg3', 'leg4'])
                time.sleep(self.movement_speed)
                
                # Phase 2: Move lifted legs forward
                self._move_legs_forward(['leg1', 'leg3', 'leg4'])
                time.sleep(self.movement_speed)
                
                # Phase 3: Lower legs
                self._lower_legs(['leg1', 'leg3', 'leg4'])
                time.sleep(self.movement_speed)
                
                # Phase 4: Lift legs 2
                self._lift_legs(['leg2'])
                time.sleep(self.movement_speed)
                
                # Phase 5: Move lifted legs forward
                self._move_legs_forward(['leg2'])
                time.sleep(self.movement_speed)
                
                # Phase 6: Lower legs
                self._lower_legs(['leg2'])
                time.sleep(self.movement_speed)
                
        finally:
            self.is_moving = False
            self.go_home()
            
    def walk_backward(self, steps: int = 3):
        """Walk backward"""
        print(f"Walking backward ({steps} steps)...")
        self.is_moving = True
        self.current_mode = "WALKING_BACK"
        
        if self.oled:
            self.oled.update_mode("WALKING")
        
        try:
            for step in range(steps):
                self._lift_legs(['leg1', 'leg3', 'leg4'])
                time.sleep(self.movement_speed)
                self._move_legs_backward(['leg1', 'leg3', 'leg4'])
                time.sleep(self.movement_speed)
                self._lower_legs(['leg1', 'leg3', 'leg4'])
                time.sleep(self.movement_speed)
                
                self._lift_legs(['leg2'])
                time.sleep(self.movement_speed)
                self._move_legs_backward(['leg2'])
                time.sleep(self.movement_speed)
                self._lower_legs(['leg2'])
                time.sleep(self.movement_speed)
                
        finally:
            self.is_moving = False
            self.go_home()
            
    def turn_left(self, angle: int = 45):
        """Turn left by rotating body"""
        print(f"Turning left ({angle} degrees)...")
        self.is_moving = True
        self.current_mode = "TURNING_LEFT"
        
        if self.oled:
            self.oled.update_mode("TURNING")
        
        try:
            steps = angle // 15
            for _ in range(steps):
                self._lift_legs(['leg1', 'leg4'])
                time.sleep(self.movement_speed)
                
                self._set_servo('leg1', 'shoulder', 
                               self.home_positions['leg1'].shoulder - self.turn_angle)
                self._set_servo('leg4', 'shoulder', 
                               self.home_positions['leg4'].shoulder + self.turn_angle)
                time.sleep(self.movement_speed)
                
                self._lower_legs(['leg1', 'leg4'])
                time.sleep(self.movement_speed)
                
                self._lift_legs(['leg2', 'leg3'])
                time.sleep(self.movement_speed)
                
                self._set_servo('leg2', 'shoulder', 
                               self.home_positions['leg2'].shoulder - self.turn_angle)
                self._set_servo('leg3', 'shoulder', 
                               self.home_positions['leg3'].shoulder + self.turn_angle)
                time.sleep(self.movement_speed)
                
                self._lower_legs(['leg2', 'leg3'])
                time.sleep(self.movement_speed)
                
        finally:
            self.is_moving = False
            self.go_home()
            
    def turn_right(self, angle: int = 45):
        """Turn right by rotating body"""
        print(f"Turning right ({angle} degrees)...")
        self.is_moving = True
        self.current_mode = "TURNING_RIGHT"
        
        if self.oled:
            self.oled.update_mode("TURNING")
        
        try:
            steps = angle // 15
            for _ in range(steps):
                self._lift_legs(['leg1', 'leg4'])
                time.sleep(self.movement_speed)
                
                self._set_servo('leg1', 'shoulder', 
                               self.home_positions['leg1'].shoulder + self.turn_angle)
                self._set_servo('leg4', 'shoulder', 
                               self.home_positions['leg4'].shoulder - self.turn_angle)
                time.sleep(self.movement_speed)
                
                self._lower_legs(['leg1', 'leg4'])
                time.sleep(self.movement_speed)
                
                self._lift_legs(['leg2', 'leg3'])
                time.sleep(self.movement_speed)
                
                self._set_servo('leg2', 'shoulder', 
                               self.home_positions['leg2'].shoulder + self.turn_angle)
                self._set_servo('leg3', 'shoulder', 
                               self.home_positions['leg3'].shoulder - self.turn_angle)
                time.sleep(self.movement_speed)
                
                self._lower_legs(['leg2', 'leg3'])
                time.sleep(self.movement_speed)
                
        finally:
            self.is_moving = False
            self.go_home()
            
    def dance(self):
        """Perform dance routine"""
        print("Dancing...")
        self.is_moving = True
        self.current_mode = "DANCING"
        
        if self.oled:
            self.oled.update_mode("DANCING")
        
        try:
            # Dance sequence
            for _ in range(3):
                # Wave motion
                for leg in ['leg1', 'leg2', 'leg3', 'leg4']:
                    self._set_servo(leg, 'elbow', 
                                   self.home_positions[leg].elbow - 30)
                    time.sleep(0.1)
                    self._set_servo(leg, 'elbow', 
                                   self.home_positions[leg].elbow)
                    time.sleep(0.1)
                    
                # Body wiggle
                for i in range(4):
                    offset = 15 if i % 2 == 0 else -15
                    for leg in self.home_positions.keys():
                        self._set_servo(leg, 'shoulder', 
                                       self.home_positions[leg].shoulder + offset)
                    time.sleep(0.2)
                    
        finally:
            self.is_moving = False
            self.go_home()
            
    def wave(self):
        """Wave with front right leg"""
        print("Waving...")
        self.is_moving = True
        self.current_mode = "WAVING"
        
        if self.oled:
            self.oled.update_mode("WAVING")
        
        try:
            # Lift leg
            self._set_servo('leg1', 'shoulder', 90)
            self._set_servo('leg1', 'elbow', 45)
            time.sleep(0.3)
            
            # Wave motion
            for _ in range(5):
                self._set_servo('leg1', 'foot', 30)
                time.sleep(0.2)
                self._set_servo('leg1', 'foot', 90)
                time.sleep(0.2)
                
        finally:
            self.is_moving = False
            self.go_home()
            
    def stop(self):
        """Emergency stop"""
        print("Emergency stop")
        self.is_moving = False
        self.current_mode = "STOPPED"
        self.go_home()
        
    def _lift_legs(self, legs: List[str]):
        """Lift specified legs"""
        for leg in legs:
            if leg in self.home_positions:
                self._set_servo(leg, 'elbow', 
                               self.home_positions[leg].elbow - self.step_height)
                
    def _lower_legs(self, legs: List[str]):
        """Lower specified legs"""
        for leg in legs:
            if leg in self.home_positions:
                self._set_servo(leg, 'elbow', self.home_positions[leg].elbow)
                
    def _move_legs_forward(self, legs: List[str]):
        """Move specified legs forward"""
        for leg in legs:
            if leg in self.home_positions:
                self._set_servo(leg, 'foot', 
                               self.home_positions[leg].foot + self.step_forward)
                
    def _move_legs_backward(self, legs: List[str]):
        """Move specified legs backward"""
        for leg in legs:
            if leg in self.home_positions:
                self._set_servo(leg, 'foot', 
                               self.home_positions[leg].foot - self.step_forward)
                
    def get_distance(self) -> float:
        """Get distance from ultrasonic sensor"""
        if not GPIO_AVAILABLE:
            import random
            distance = random.uniform(10, 100)
            if self.oled:
                self.oled.update_distance(distance)
            return distance
            
        try:
            GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.LOW)
            
            pulse_start = time.time()
            pulse_end = time.time()
            timeout = time.time() + 0.1
            
            while GPIO.input(ULTRASONIC_PINS['echo']) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start > timeout:
                    return 0.0
                    
            while GPIO.input(ULTRASONIC_PINS['echo']) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end > timeout:
                    return 0.0
                    
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            
            if self.oled:
                self.oled.update_distance(distance)
                
            return distance
            
        except Exception as e:
            print(f"Ultrasonic sensor error: {e}")
            return 0.0
            
    def cleanup(self):
        """Cleanup hardware resources"""
        print("Cleaning up spider controller...")
        
        try:
            self.go_home()
        except:
            pass
            
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                print("   GPIO cleaned up")
            except:
                pass
                
        print("   Spider controller cleanup complete")