"""
Hardware Configuration - GPIO Pin Mappings
For Raspberry Pi with 12-servo spider robot and OV5647 camera
"""

# ============================================
# I2C Device Addresses
# ============================================
I2C_ADDRESSES = {
    'pca9685': 0x40,    # Servo controller (default)
    'oled': 0x3C,       # OLED display (common address)
}

# ============================================
# GPIO Pin Assignments
# ============================================
ULTRASONIC_PINS = {
    'trigger': 23,      # GPIO 23
    'echo': 24,         # GPIO 24
}

# ============================================
# Servo Mappings (PCA9685)
# 16 channels available
# ============================================
SERVO_PINS = {
    # Front Right Leg (Leg 1)
    'leg1_shoulder': 0,  # Channel 0
    'leg1_elbow': 1,     # Channel 1
    'leg1_foot': 2,      # Channel 2
    
    # Front Left Leg (Leg 2)
    'leg2_shoulder': 3,  # Channel 3
    'leg2_elbow': 4,     # Channel 4
    'leg2_foot': 5,      # Channel 5
    
    # Back Right Leg (Leg 3)
    'leg3_shoulder': 6,  # Channel 6
    'leg3_elbow': 7,     # Channel 7
    'leg3_foot': 8,      # Channel 8
    
    # Back Left Leg (Leg 4)
    'leg4_shoulder': 9,  # Channel 9
    'leg4_elbow': 10,    # Channel 10
    'leg4_foot': 11,     # Channel 11
    
    # Extra servos (if needed)
    'servo12': 12,
    'servo13': 13,
    'servo14': 14,
    'servo15': 15,
}

# ============================================
# Camera Configuration (OV5647)
# ============================================
CAMERA_CONFIG = {
    'sensor': 'OV5647',
    'width': 640,
    'height': 480,
    'fps': 30,
    'rotation': 0,      # 0, 90, 180, 270
    'flip_horizontal': False,
    'flip_vertical': False,
    'brightness': 50,
    'contrast': 0,
    'saturation': 0,
}

# ============================================
# I2C Configuration
# ============================================
I2C_CONFIG = {
    'bus': 1,           # I2C bus 1 (default on Raspberry Pi)
    'speed': 400000,    # 400kHz
    'timeout': 5,
}

# ============================================
# Servo Limits and Ranges
# ============================================
SERVO_LIMITS = {
    'min_angle': 0,
    'max_angle': 180,
    'min_pulse': 500,    # Microseconds
    'max_pulse': 2500,   # Microseconds
    'frequency': 50,     # Hz
    'actuation_range': 180,
}

# ============================================
# Movement Parameters
# ============================================
MOVEMENT_PARAMS = {
    'step_height': 30,        # degrees
    'step_forward': 20,       # degrees
    'turn_angle': 15,         # degrees
    'movement_speed': 0.02,   # seconds
    'gait_type': 'tripod',    # tripod or wave
}

# ============================================
# Sensor Configuration
# ============================================
SENSOR_CONFIG = {
    'ultrasonic': {
        'max_distance': 400,    # cm
        'min_distance': 2,      # cm
        'timeout': 0.1,         # seconds
        'speed_of_sound': 34300, # cm/s at 25°C
    },
    'oled': {
        'width': 128,
        'height': 64,
        'address': 0x3C,
        'bus': 1,
    }
}

# ============================================
# Pin Verification
# ============================================
def verify_pins():
    """Verify all pin assignments are valid"""
    used_servo_channels = set(SERVO_PINS.values())
    max_channel = max(used_servo_channels)
    
    if max_channel > 15:
        raise ValueError(f"Servo channel {max_channel} exceeds PCA9685 capacity (0-15)")
    
    # Check no duplicate channels
    if len(used_servo_channels) != len(SERVO_PINS):
        raise ValueError("Duplicate servo channels detected")
    
    return True


if __name__ == "__main__":
    verify_pins()
    print("✅ Pin configuration verified")
    print(f"   Servos: {len(SERVO_PINS)} channels")
    print(f"   Max channel: {max(SERVO_PINS.values())}")