"""
Hey Spider Robot - Test Package
Unit and integration tests for all components
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test configuration
TEST_DATA_DIR = PROJECT_ROOT / "data" / "test"
TEST_IMAGES_DIR = PROJECT_ROOT / "images" / "test"
TEST_LOGS_DIR = PROJECT_ROOT / "logs" / "test"

# Create test directories
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
TEST_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Test utilities
class MockHardware:
    """Mock hardware for testing without actual devices"""
    
    @staticmethod
    def mock_gpio():
        """Mock GPIO module"""
        class MockGPIO:
            BCM = 0
            OUT = 0
            IN = 1
            HIGH = 1
            LOW = 0
            
            @staticmethod
            def setmode(mode):
                pass
            
            @staticmethod
            def setup(pin, mode):
                pass
            
            @staticmethod
            def output(pin, state):
                pass
            
            @staticmethod
            def input(pin):
                return 0
            
            @staticmethod
            def cleanup():
                pass
        
        return MockGPIO
    
    @staticmethod
    def mock_servokit():
        """Mock ServoKit for testing"""
        class MockServo:
            def __init__(self):
                self._angle = 90
            
            @property
            def angle(self):
                return self._angle
            
            @angle.setter
            def angle(self, value):
                self._angle = max(0, min(180, value))
        
        class MockServoKit:
            def __init__(self, channels=16):
                self.servo = [MockServo() for _ in range(channels)]
        
        return MockServoKit
    
    @staticmethod
    def mock_camera():
        """Mock camera for testing"""
        import numpy as np
        
        class MockCamera:
            def __init__(self):
                self.is_active = True
                self.width = 640
                self.height = 480
            
            def get_frame(self):
                return np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            def release(self):
                pass
        
        return MockCamera()


# Environment setup for tests
os.environ['MOCK_HARDWARE'] = 'true'
os.environ['DEBUG_MODE'] = 'false'
os.environ['LOG_LEVEL'] = 'WARNING'

__all__ = [
    'MockHardware',
    'TEST_DATA_DIR',
    'TEST_IMAGES_DIR',
    'TEST_LOGS_DIR',
]