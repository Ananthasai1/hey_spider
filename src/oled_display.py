"""
OLED Display Manager - 128x64 SSD1306 Display
Shows real-time robot status, detections, and AI thoughts
"""

import threading
import time
from datetime import datetime
from typing import List, Dict, Optional

try:
    import board
    import busio
    import adafruit_ssd1306
    from PIL import Image, ImageDraw, ImageFont
    OLED_AVAILABLE = True
except ImportError:
    print("⚠️  OLED libraries not available - using mock display")
    OLED_AVAILABLE = False

from config.hardware_config import I2C_CONFIG, SENSOR_CONFIG


class OLEDDisplay:
    """OLED display controller with threaded updates"""
    
    def __init__(self):
        self.display = None
        self.running = False
        self.thread = None
        
        # Display data
        self.mode = "INIT"
        self.distance = 0.0
        self.detections = []
        self.ai_thought = "Initializing..."
        self.command = "--"
        self.fps = 0
        
        # Status
        self.update_lock = threading.Lock()
        self.last_update = time.time()
        
        # Fonts
        self.font_large = None
        self.font_small = None
        
        # Initialize hardware
        self._initialize_display()
        
    def _initialize_display(self):
        """Initialize OLED display"""
        if not OLED_AVAILABLE:
            print("⚠️  OLED in mock mode")
            self._create_mock_display()
            return
        
        try:
            print("📡 Initializing OLED display...")
            
            # Initialize I2C
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize display
            addr = SENSOR_CONFIG['oled']['address']
            self.display = adafruit_ssd1306.SSD1306_I2C(
                SENSOR_CONFIG['oled']['width'],
                SENSOR_CONFIG['oled']['height'],
                i2c,
                addr=addr
            )
            
            # Load fonts
            try:
                self.font_large = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
                )
                self.font_small = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10
                )
            except:
                self.font_large = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            
            print("✅ OLED display initialized")
            
        except Exception as e:
            print(f"❌ OLED initialization failed: {e}")
            self._create_mock_display()
    
    def _create_mock_display(self):
        """Create mock display for testing"""
        class MockDisplay:
            def __init__(self):
                self.width = 128
                self.height = 64
                self.image = None
                
            def fill(self, color):
                pass
            
            def show(self):
                pass
            
            def image(self, img):
                self.image = img
        
        self.display = MockDisplay()
    
    def show_startup_message(self):
        """Show startup message"""
        if not self.display:
            return
        
        try:
            image = Image.new('1', (128, 64))
            draw = ImageDraw.Draw(image)
            
            draw.text((10, 5), "HEY SPIDER", font=self.font_large, fill=255)
            draw.text((10, 25), "Robot v2.0", font=self.font_small, fill=255)
            draw.text((10, 38), "Initializing...", font=self.font_small, fill=255)
            draw.text((10, 50), "Please wait", font=self.font_small, fill=255)
            
            self.display.image(image)
            self.display.show()
            
        except Exception as e:
            print(f"❌ Startup message error: {e}")
    
    def start(self):
        """Start display update thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print("✅ OLED display thread started")
    
    def stop(self):
        """Stop display update thread"""
        print("🛑 Stopping OLED display...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.display:
            try:
                self.display.fill(0)
                self.display.show()
            except:
                pass
        
        print("✅ OLED display stopped")
    
    def _update_loop(self):
        """Update display periodically"""
        while self.running:
            try:
                self._render_display()
                time.sleep(0.5)  # Update every 500ms
            except Exception as e:
                print(f"❌ Display update error: {e}")
                time.sleep(1)
    
    def _render_display(self):
        """Render current display content"""
        if not self.display:
            return
        
        try:
            image = Image.new('1', (128, 64))
            draw = ImageDraw.Draw(image)
            
            with self.update_lock:
                # Line 1: Mode
                mode_text = f"Mode: {self.mode:8}"
                draw.text((0, 0), mode_text, font=self.font_small, fill=255)
                
                # Line 2: Distance
                dist_text = f"Dist: {self.distance:6.1f}cm"
                draw.text((0, 10), dist_text, font=self.font_small, fill=255)
                
                # Line 3: Detections
                det_text = f"Sees: {len(self.detections):2} objects"
                draw.text((0, 20), det_text, font=self.font_small, fill=255)
                
                # Line 4: Command
                cmd_text = f"Cmd: {self.command:15}"
                draw.text((0, 30), cmd_text, font=self.font_small, fill=255)
                
                # Line 5: AI Thought (scrolling)
                thought = self.ai_thought[:22]  # Truncate
                draw.text((0, 40), thought, font=self.font_small, fill=255)
                
                # Line 6: FPS
                fps_text = f"FPS: {self.fps:3.0f}"
                draw.text((0, 50), fps_text, font=self.font_small, fill=255)
                
                # Time
                time_text = datetime.now().strftime("%H:%M:%S")
                draw.text((90, 50), time_text, font=self.font_small, fill=255)
            
            self.display.image(image)
            self.display.show()
            
        except Exception as e:
            print(f"❌ Render error: {e}")
    
    def update_mode(self, mode: str):
        """Update robot mode"""
        with self.update_lock:
            self.mode = mode[:10]  # Truncate
    
    def update_distance(self, distance: float):
        """Update distance reading"""
        with self.update_lock:
            self.distance = max(0, min(999.9, distance))
    
    def update_detections(self, detections: List[Dict]):
        """Update detected objects"""
        with self.update_lock:
            self.detections = detections[:5]  # Keep last 5
    
    def update_command(self, command: str):
        """Update current command"""
        with self.update_lock:
            self.command = command[:15]  # Truncate
    
    def update_thought(self, thought: str):
        """Update AI thought"""
        with self.update_lock:
            self.ai_thought = thought[:30]  # Truncate
    
    def update_fps(self, fps: float):
        """Update FPS counter"""
        with self.update_lock:
            self.fps = fps
    
    def show_message(self, line1: str, line2: str = "", line3: str = ""):
        """Show temporary message"""
        if not self.display:
            return
        
        try:
            image = Image.new('1', (128, 64))
            draw = ImageDraw.Draw(image)
            
            draw.text((5, 10), line1[:20], font=self.font_large, fill=255)
            if line2:
                draw.text((5, 30), line2[:20], font=self.font_small, fill=255)
            if line3:
                draw.text((5, 45), line3[:20], font=self.font_small, fill=255)
            
            self.display.image(image)
            self.display.show()
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Message display error: {e}")
    
    def show_error(self, error_msg: str):
        """Show error message"""
        self.show_message("ERROR!", error_msg[:15])
    
    def show_success(self, msg: str):
        """Show success message"""
        self.show_message("SUCCESS!", msg[:15])
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop()
        print("✅ OLED display cleanup complete")