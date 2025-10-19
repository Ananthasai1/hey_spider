"""
Hey Spider Robot - Settings Configuration
Complete settings management with environment variable support
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")


@dataclass
class Settings:
    """Application settings with defaults"""
    
    # ============================================
    # API Configuration
    # ============================================
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    AI_MODEL: str = os.getenv('AI_MODEL', 'gpt-4')
    
    # ============================================
    # Voice Settings
    # ============================================
    WAKE_PHRASE: str = os.getenv('WAKE_PHRASE', 'hey spider').lower()
    VOICE_TIMEOUT: int = int(os.getenv('VOICE_TIMEOUT', '5'))
    VOICE_LANGUAGE: str = os.getenv('VOICE_LANGUAGE', 'en-US')
    
    # ============================================
    # Vision Settings
    # ============================================
    CAMERA_ENABLED: bool = os.getenv('CAMERA_ENABLED', 'true').lower() == 'true'
    AUTO_CAPTURE_INTERVAL: int = int(os.getenv('AUTO_CAPTURE_INTERVAL', '30'))
    CONFIDENCE_THRESHOLD: float = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
    CAMERA_WIDTH: int = int(os.getenv('CAMERA_WIDTH', '640'))
    CAMERA_HEIGHT: int = int(os.getenv('CAMERA_HEIGHT', '480'))
    CAMERA_FPS: int = int(os.getenv('CAMERA_FPS', '30'))
    
    # ============================================
    # YOLO Configuration
    # ============================================
    YOLO_MODEL: str = os.getenv('YOLO_MODEL', 'yolov8n.pt')
    USE_YOLO_V12: bool = os.getenv('USE_YOLO_V12', 'false').lower() == 'true'
    YOLO_DEVICE: str = os.getenv('YOLO_DEVICE', 'auto')  # auto, cpu, cuda
    DETECTION_INTERVAL: float = float(os.getenv('DETECTION_INTERVAL', '0.1'))
    MAX_DETECTIONS: int = int(os.getenv('MAX_DETECTIONS', '20'))
    IOU_THRESHOLD: float = float(os.getenv('IOU_THRESHOLD', '0.4'))
    
    # ============================================
    # AI Thinking Settings
    # ============================================
    AI_THINKING_INTERVAL: int = int(os.getenv('AI_THINKING_INTERVAL', '15'))
    AI_TEMPERATURE: float = float(os.getenv('AI_TEMPERATURE', '0.8'))
    AI_MAX_TOKENS: int = int(os.getenv('AI_MAX_TOKENS', '150'))
    
    # ============================================
    # Web Interface Settings
    # ============================================
    WEB_PORT: int = int(os.getenv('WEB_PORT', '5000'))
    WEB_HOST: str = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_DEBUG: bool = os.getenv('WEB_DEBUG', 'false').lower() == 'true'
    SOCKETIO_PING_TIMEOUT: int = int(os.getenv('SOCKETIO_PING_TIMEOUT', '60'))
    SOCKETIO_PING_INTERVAL: int = int(os.getenv('SOCKETIO_PING_INTERVAL', '25'))
    
    # ============================================
    # Hardware Settings
    # ============================================
    SERVO_FREQUENCY: int = int(os.getenv('SERVO_FREQUENCY', '50'))
    SERVO_MIN_PULSE: int = int(os.getenv('SERVO_MIN_PULSE', '500'))
    SERVO_MAX_PULSE: int = int(os.getenv('SERVO_MAX_PULSE', '2500'))
    SERVO_ACTUATION_RANGE: int = int(os.getenv('SERVO_ACTUATION_RANGE', '180'))
    
    # Movement parameters
    STEP_HEIGHT: int = int(os.getenv('STEP_HEIGHT', '30'))
    STEP_FORWARD: int = int(os.getenv('STEP_FORWARD', '20'))
    TURN_ANGLE: int = int(os.getenv('TURN_ANGLE', '15'))
    MOVEMENT_SPEED: float = float(os.getenv('MOVEMENT_SPEED', '0.02'))
    
    # Ultrasonic settings
    ULTRASONIC_MAX_DISTANCE: int = int(os.getenv('ULTRASONIC_MAX_DISTANCE', '400'))
    ULTRASONIC_TIMEOUT: float = float(os.getenv('ULTRASONIC_TIMEOUT', '0.1'))
    
    # ============================================
    # OLED Display Settings
    # ============================================
    OLED_WIDTH: int = int(os.getenv('OLED_WIDTH', '128'))
    OLED_HEIGHT: int = int(os.getenv('OLED_HEIGHT', '64'))
    OLED_UPDATE_INTERVAL: float = float(os.getenv('OLED_UPDATE_INTERVAL', '0.5'))
    OLED_I2C_ADDRESS: int = int(os.getenv('OLED_I2C_ADDRESS', '0x3C'), 16)
    
    # ============================================
    # Logging Settings
    # ============================================
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/spider.log')
    LOG_MAX_SIZE: int = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # ============================================
    # File Paths
    # ============================================
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    IMAGES_DIR: Path = PROJECT_ROOT / 'images'
    MODELS_DIR: Path = PROJECT_ROOT / 'models'
    LOGS_DIR: Path = PROJECT_ROOT / 'logs'
    DATA_DIR: Path = PROJECT_ROOT / 'data'
    
    # ============================================
    # Performance Settings
    # ============================================
    ENABLE_PERFORMANCE_TRACKING: bool = os.getenv('ENABLE_PERFORMANCE_TRACKING', 'true').lower() == 'true'
    MOCK_HARDWARE: bool = os.getenv('MOCK_HARDWARE', 'false').lower() == 'true'
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # ============================================
    # Safety Settings
    # ============================================
    SERVO_SAFE_MIN: int = int(os.getenv('SERVO_SAFE_MIN', '0'))
    SERVO_SAFE_MAX: int = int(os.getenv('SERVO_SAFE_MAX', '180'))
    OBSTACLE_STOP_DISTANCE: int = int(os.getenv('OBSTACLE_STOP_DISTANCE', '15'))  # cm
    
    def __post_init__(self):
        """Validate settings after initialization"""
        # Create directories if they don't exist
        for directory in [self.IMAGES_DIR, self.MODELS_DIR, self.LOGS_DIR, self.DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Validate API key
        if not self.OPENAI_API_KEY and not self.MOCK_HARDWARE:
            print("⚠️  WARNING: OPENAI_API_KEY not set!")
            print("   AI features will be limited.")
            print("   Set your API key in .env file")
        
        # Validate ranges
        if not (0.0 <= self.CONFIDENCE_THRESHOLD <= 1.0):
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
        
        if not (0.0 <= self.IOU_THRESHOLD <= 1.0):
            raise ValueError("IOU_THRESHOLD must be between 0.0 and 1.0")
        
        if self.WEB_PORT < 1024 or self.WEB_PORT > 65535:
            raise ValueError("WEB_PORT must be between 1024 and 65535")
    
    def get_model_path(self) -> Path:
        """Get full path to YOLO model"""
        model_path = self.MODELS_DIR / self.YOLO_MODEL
        if not model_path.exists():
            # Try project root
            alt_path = self.PROJECT_ROOT / self.YOLO_MODEL
            if alt_path.exists():
                return alt_path
        return model_path
    
    def is_api_configured(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.startswith('sk-'))
    
    def get_log_path(self) -> Path:
        """Get full path to log file"""
        log_path = Path(self.LOG_FILE)
        if not log_path.is_absolute():
            log_path = self.PROJECT_ROOT / log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary"""
        return {
            'api': {
                'openai_configured': self.is_api_configured(),
                'model': self.AI_MODEL,
            },
            'voice': {
                'wake_phrase': self.WAKE_PHRASE,
                'timeout': self.VOICE_TIMEOUT,
            },
            'vision': {
                'camera_enabled': self.CAMERA_ENABLED,
                'resolution': f"{self.CAMERA_WIDTH}x{self.CAMERA_HEIGHT}",
                'fps': self.CAMERA_FPS,
            },
            'yolo': {
                'model': self.YOLO_MODEL,
                'confidence': self.CONFIDENCE_THRESHOLD,
                'device': self.YOLO_DEVICE,
            },
            'web': {
                'host': self.WEB_HOST,
                'port': self.WEB_PORT,
            },
            'hardware': {
                'servo_frequency': self.SERVO_FREQUENCY,
                'mock_mode': self.MOCK_HARDWARE,
            },
        }


# Global settings instance
settings = Settings()


# Validation on import
if __name__ != "__main__":
    if settings.DEBUG_MODE:
        print("🔧 Settings loaded in DEBUG mode")
        print(f"   Project Root: {settings.PROJECT_ROOT}")
        print(f"   API Configured: {settings.is_api_configured()}")
        print(f"   Camera: {'Enabled' if settings.CAMERA_ENABLED else 'Disabled'}")
        print(f"   Web Port: {settings.WEB_PORT}")