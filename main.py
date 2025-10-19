#!/usr/bin/env python3
"""
🕷️ Hey Spider Robot - Main Application
Version 2.0 - Complete Rewrite with Modern Architecture

Features:
- Auto-starting camera system
- Real-time YOLO object detection
- AI-powered reasoning with OpenAI GPT
- Voice command activation
- Beautiful web dashboard
- OLED status display
- Comprehensive error handling
"""

import sys
import time
import signal
import json
import traceback
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings

# ASCII Art Banner
BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🕷️  HEY SPIDER ROBOT v2.0 🕷️                   ║
║                                                           ║
║     AI-Powered Quadruped with Real-Time Vision           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

class HeySpiderRobot:
    """Main robot controller with comprehensive initialization"""
    
    def __init__(self):
        print(BANNER)
        print(f"🐍 Python {sys.version}")
        print(f"📁 Working Directory: {os.getcwd()}")
        print(f"🔑 OpenAI API Key: {'✓ Configured' if settings.OPENAI_API_KEY else '✗ Missing'}")
        print("=" * 63)
        
        # Component references
        self.oled = None
        self.spider = None
        self.vision = None
        self.ai = None
        self.voice = None
        self.web = None
        self.running = False
        
        # Statistics
        self.start_time = datetime.now()
        self.stats = {
            'commands_processed': 0,
            'photos_captured': 0,
            'detections_made': 0,
            'errors': 0
        }
        
        # Initialize all components
        self._initialize_components()
        
        print("=" * 63)
        print("✅ INITIALIZATION COMPLETE")
        print("=" * 63)
        
    def _initialize_components(self):
        """Initialize all robot components with error handling"""
        
        # 1. OLED Display (first for visual feedback)
        print("\n[1/6] 📺 Initializing OLED Display...")
        try:
            from src.oled_display import OLEDDisplay
            self.oled = OLEDDisplay()
            if self.oled.display:
                self.oled.show_startup_message()
                self.oled.start()
                print("     ✅ OLED display active")
            else:
                print("     ⚠️  OLED display in mock mode")
        except Exception as e:
            print(f"     ❌ OLED initialization failed: {e}")
            self.oled = None
            
        # 2. Spider Controller (hardware interface)
        print("\n[2/6] 🤖 Initializing Spider Controller...")
        try:
            from src.spider_controller import SpiderController
            self.spider = SpiderController(self.oled)
            print("     ✅ Spider controller ready")
        except Exception as e:
            print(f"     ❌ Spider controller failed: {e}")
            traceback.print_exc()
            self.spider = None
            
        # 3. Visual Monitor (camera + YOLO)
        print("\n[3/6] 📹 Initializing Visual Monitoring System...")
        try:
            # Try enhanced monitor first (YOLOv12)
            try:
                from src.enhanced_visual_monitor import VisualMonitor
                print("     Using Enhanced Visual Monitor (YOLOv12)")
            except ImportError:
                from src.visual_monitor import VisualMonitor
                print("     Using Standard Visual Monitor (YOLOv8)")
                
            self.vision = VisualMonitor(self.oled)
            
            # Auto-start camera
            print("     🎥 Auto-starting camera...")
            if self.vision.camera_active:
                print("     ✅ Camera system active")
            else:
                print("     ⚠️  Camera in mock mode")
                
        except Exception as e:
            print(f"     ❌ Visual monitoring failed: {e}")
            traceback.print_exc()
            self.vision = None
            
        # 4. AI Thinking (OpenAI integration)
        print("\n[4/6] 🧠 Initializing AI Thinking Engine...")
        try:
            from src.ai_thinking import AIThinking
            self.ai = AIThinking(self.spider, self.vision, self.oled)
            
            if self.ai.client:
                print("     ✅ AI engine connected to OpenAI")
            else:
                print("     ⚠️  AI engine in offline mode")
                
        except Exception as e:
            print(f"     ❌ AI initialization failed: {e}")
            traceback.print_exc()
            self.ai = None
            
        # 5. Voice Activation (speech recognition)
        print("\n[5/6] 🎙️  Initializing Voice Activation...")
        try:
            from src.voice_activation import VoiceActivation
            self.voice = VoiceActivation(self.handle_voice_command, self.oled)
            
            if self.voice.recognizer:
                print("     ✅ Voice recognition active")
            else:
                print("     ⚠️  Voice system in mock mode")
                
        except Exception as e:
            print(f"     ❌ Voice activation failed: {e}")
            traceback.print_exc()
            self.voice = None
            
        # 6. Web Interface (Flask + SocketIO)
        print("\n[6/6] 🌐 Initializing Web Interface...")
        try:
            from src.web_interface import WebInterface
            self.web = WebInterface(self.spider, self.vision, self.ai, self.oled)
            print(f"     ✅ Web interface ready on port {settings.WEB_PORT}")
        except Exception as e:
            print(f"     ❌ Web interface failed: {e}")
            traceback.print_exc()
            self._create_fallback_web()
            
    def _create_fallback_web(self):
        """Create minimal fallback web interface"""
        try:
            print("     🔄 Creating fallback web interface...")
            from flask import Flask, jsonify, render_template_string
            
            class MinimalWeb:
                def __init__(self, spider, vision, ai):
                    self.app = Flask(__name__)
                    self.spider = spider
                    self.vision = vision
                    self.ai = ai
                    self.setup_routes()
                    
                def setup_routes(self):
                    @self.app.route('/')
                    def index():
                        return render_template_string("""
                        <html>
                        <head><title>Hey Spider Robot - Minimal Mode</title></head>
                        <body style="font-family: Arial; padding: 20px; background: #0a0e27; color: white;">
                            <h1>🕷️ Hey Spider Robot</h1>
                            <p>Running in minimal mode due to initialization errors.</p>
                            <h2>Status:</h2>
                            <ul>
                                <li>Spider Controller: {{ 'OK' if spider else 'Error' }}</li>
                                <li>Vision System: {{ 'OK' if vision else 'Error' }}</li>
                                <li>AI System: {{ 'OK' if ai else 'Error' }}</li>
                            </ul>
                        </body>
                        </html>
                        """, spider=self.spider, vision=self.vision, ai=self.ai)
                        
                    @self.app.route('/health')
                    def health():
                        return jsonify({
                            'status': 'minimal_mode',
                            'spider': bool(self.spider),
                            'vision': bool(self.vision),
                            'ai': bool(self.ai)
                        })
                        
                def run(self, host='0.0.0.0', port=5000, debug=False):
                    self.app.run(host=host, port=port, debug=debug)
                    
            self.web = MinimalWeb(self.spider, self.vision, self.ai)
            print("     ✅ Fallback web interface created")
            
        except Exception as e:
            print(f"     ❌ Even fallback failed: {e}")
            self.web = None
            
    def handle_voice_command(self, command: str):
        """Process voice commands with comprehensive handling"""
        print(f"\n🎤 Voice Command: '{command}'")
        self.stats['commands_processed'] += 1
        
        try:
            if self.oled:
                self.oled.update_command(command)
                self.oled.update_mode("PROCESSING")
                
            command = command.lower().strip()
            
            # Movement commands
            if any(word in command for word in ['forward', 'walk', 'move', 'ahead']):
                if self.spider:
                    self.spider.walk_forward()
                    self._speak_response("Moving forward")
                    
            elif 'back' in command or 'backward' in command:
                if self.spider:
                    self.spider.walk_backward()
                    self._speak_response("Moving backward")
                    
            elif 'left' in command:
                if self.spider:
                    self.spider.turn_left()
                    self._speak_response("Turning left")
                    
            elif 'right' in command:
                if self.spider:
                    self.spider.turn_right()
                    self._speak_response("Turning right")
                    
            # Action commands
            elif 'dance' in command:
                if self.spider:
                    self.spider.dance()
                    self._speak_response("Let me dance for you!")
                    
            elif 'wave' in command or 'hello' in command:
                if self.spider:
                    self.spider.wave()
                    self._speak_response("Hello there!")
                    
            elif 'sit' in command:
                if self.spider:
                    self.spider.sit_down()
                    self._speak_response("Sitting down")
                    
            elif 'stand' in command:
                if self.spider:
                    self.spider.stand_up()
                    self._speak_response("Standing up")
                    
            # Camera commands
            elif any(word in command for word in ['photo', 'picture', 'capture', 'snapshot']):
                if self.vision:
                    filename = self.vision.capture_photo()
                    if filename:
                        self.stats['photos_captured'] += 1
                        self._speak_response("Photo captured successfully")
                        print(f"     📸 Saved: {filename}")
                    else:
                        self._speak_response("Photo capture failed")
                        
            elif 'what' in command and 'see' in command:
                if self.vision:
                    description = self.vision.get_detection_description()
                    self._speak_response(description)
                    print(f"     👁️  {description}")
                    
            elif 'stop' in command:
                if self.spider:
                    self.spider.stop()
                self._speak_response("Stopped")
                if self.oled:
                    self.oled.update_mode("STOPPED")
                    
            # AI-processed commands
            else:
                if self.ai and self.ai.client:
                    try:
                        ai_response = self.ai.process_command(command)
                        parsed = json.loads(ai_response)
                        action = parsed.get('action', 'unknown')
                        response = parsed.get('response', 'Command processed')
                        
                        print(f"     🤖 AI: {response}")
                        self._speak_response(response)
                        
                        # Execute AI-determined action
                        action_map = {
                            'walk_forward': lambda: self.spider.walk_forward() if self.spider else None,
                            'turn_left': lambda: self.spider.turn_left() if self.spider else None,
                            'turn_right': lambda: self.spider.turn_right() if self.spider else None,
                            'dance': lambda: self.spider.dance() if self.spider else None,
                            'wave': lambda: self.spider.wave() if self.spider else None,
                            'take_photo': lambda: self.vision.capture_photo() if self.vision else None
                        }
                        
                        if action in action_map:
                            action_map[action]()
                            
                    except Exception as e:
                        print(f"     ❌ AI processing error: {e}")
                        self._speak_response("I couldn't understand that command")
                else:
                    print(f"     ⚠️  Unknown command (AI not available)")
                    self._speak_response("I don't understand that command")
                    
        except Exception as e:
            print(f"     ❌ Command execution error: {e}")
            traceback.print_exc()
            self.stats['errors'] += 1
            if self.oled:
                self.oled.update_mode("ERROR")
                time.sleep(2)
                
        finally:
            if self.oled:
                self.oled.update_mode("LISTENING")
                
    def _speak_response(self, text: str):
        """Speak response (placeholder for TTS)"""
        print(f"     💬 Response: {text}")
        
    def start(self):
        """Start all robot systems"""
        print("\n" + "=" * 63)
        print("🚀 STARTING HEY SPIDER ROBOT SYSTEMS")
        print("=" * 63)
        
        self.running = True
        available_systems = []
        
        # Start subsystems
        if self.vision:
            try:
                self.vision.start_monitoring()
                available_systems.append("✅ Visual Monitoring")
            except Exception as e:
                print(f"❌ Visual monitoring start failed: {e}")
                
        if self.ai:
            try:
                self.ai.start_thinking()
                available_systems.append("✅ AI Thinking")
            except Exception as e:
                print(f"❌ AI thinking start failed: {e}")
                
        if self.voice:
            try:
                self.voice.start_listening()
                available_systems.append("✅ Voice Activation")
            except Exception as e:
                print(f"❌ Voice activation start failed: {e}")
                
        if self.oled:
            self.oled.update_mode("ACTIVE")
            
        # Print status
        print("\n" + "=" * 63)
        print("🎉 HEY SPIDER ROBOT IS NOW ACTIVE!")
        print("=" * 63)
        
        for system in available_systems:
            print(f"  {system}")
            
        print(f"\n🤖 Spider Controller: {'Ready' if self.spider else 'Unavailable'}")
        print(f"📹 Camera: {'ACTIVE' if self.vision and self.vision.camera_active else 'INACTIVE'}")
        print(f"🌐 Web Interface: http://0.0.0.0:{settings.WEB_PORT}")
        
        if available_systems:
            print("\n📢 Voice Commands: Say 'Hey Spider' + command")
            print("⌨️  Keyboard: W/↑=forward, A/←=left, D/→=right, Space=dance, P=photo")
        
        print("\n" + "=" * 63)
        print("Press Ctrl+C to stop")
        print("=" * 63 + "\n")
        
        # Start web interface (blocking)
        if self.web:
            try:
                self.web.run(host='0.0.0.0', port=settings.WEB_PORT, debug=False)
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"❌ Web interface error: {e}")
                traceback.print_exc()
                self.stop()
        else:
            print("❌ No web interface available")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
                
    def stop(self):
        """Stop all robot systems gracefully"""
        print("\n" + "=" * 63)
        print("🛑 STOPPING HEY SPIDER ROBOT")
        print("=" * 63)
        
        self.running = False
        
        if self.oled:
            self.oled.update_mode("SHUTDOWN")
            
        # Stop subsystems
        subsystems = [
            ("Voice", self.voice, 'stop_listening'),
            ("Vision", self.vision, 'stop_monitoring'),
            ("AI", self.ai, 'stop_thinking'),
            ("OLED", self.oled, 'stop')
        ]
        
        for name, system, method in subsystems:
            if system:
                try:
                    print(f"  Stopping {name}...")
                    getattr(system, method)()
                except Exception as e:
                    print(f"  ❌ {name} shutdown error: {e}")
                    
        # Cleanup hardware
        if self.spider:
            try:
                print("  Cleaning up hardware...")
                self.spider.cleanup()
            except Exception as e:
                print(f"  ❌ Hardware cleanup error: {e}")
                
        if self.vision:
            try:
                self.vision.cleanup()
            except Exception as e:
                print(f"  ❌ Vision cleanup error: {e}")
                
        # Print statistics
        runtime = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "=" * 63)
        print("📊 SESSION STATISTICS")
        print("=" * 63)
        print(f"  Runtime: {runtime:.1f} seconds")
        print(f"  Commands Processed: {self.stats['commands_processed']}")
        print(f"  Photos Captured: {self.stats['photos_captured']}")
        print(f"  Errors: {self.stats['errors']}")
        print("=" * 63)
        print("✅ Hey Spider Robot stopped safely")
        print("=" * 63)
        
    def signal_handler(self, signum, frame):
        """Handle system signals"""
        print(f"\n🛑 Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point with comprehensive error handling"""
    print("🕷️ HEY SPIDER ROBOT v2.0 - Starting...")
    
    try:
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7+ required")
            sys.exit(1)
            
        # Check virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            print("✅ Running in virtual environment")
        else:
            print("⚠️  Not in virtual environment (recommended)")
            
        # Create necessary directories
        directories = ['images', 'images/raw', 'images/detections', 
                      'images/night_vision', 'logs', 'data', 'models']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
        # Initialize robot
        robot = HeySpiderRobot()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, robot.signal_handler)
        signal.signal(signal.SIGTERM, robot.signal_handler)
        
        # Start the robot
        robot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()