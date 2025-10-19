"""
Hey Spider Robot - Main Package
Complete AI-powered quadruped robot system
"""

__version__ = "2.0.0"
__author__ = "Hey Spider Team"
__description__ = "AI-Powered Quadruped Robot with Real-Time Vision"

# Import main components for easy access
try:
    from src.spider_controller import SpiderController
except ImportError:
    SpiderController = None

try:
    from src.camera_ov5647 import OV5647Camera
except ImportError:
    OV5647Camera = None

try:
    from src.visual_monitor import VisualMonitor
except ImportError:
    VisualMonitor = None

try:
    from src.ai_thinking import AIThinking
except ImportError:
    AIThinking = None

try:
    from src.voice_activation import VoiceActivation
except ImportError:
    VoiceActivation = None

try:
    from src.oled_display import OLEDDisplay
except ImportError:
    OLEDDisplay = None

try:
    from src.web_interface import WebInterface
except ImportError:
    WebInterface = None

__all__ = [
    'SpiderController',
    'OV5647Camera',
    'VisualMonitor',
    'AIThinking',
    'VoiceActivation',
    'OLEDDisplay',
    'WebInterface',
]