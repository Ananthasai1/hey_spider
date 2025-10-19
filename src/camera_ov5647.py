"""
OV5647 Camera Handler
Raspberry Pi camera module handler with libcamera support
"""

import threading
import time
import numpy as np
from typing import Optional
from datetime import datetime

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("⚠️  OpenCV not available")
    OPENCV_AVAILABLE = False

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    print("⚠️  Picamera2 not available")
    PICAMERA2_AVAILABLE = False

try:
    from picamera import PiCamera
    import io
    PICAMERA_LEGACY = True
except ImportError:
    print("⚠️  PiCamera legacy not available")
    PICAMERA_LEGACY = False

from config.hardware_config import CAMERA_CONFIG


class OV5647Camera:
    """OV5647 camera handler with automatic fallback"""
    
    def __init__(self):
        self.camera = None
        self.camera_type = None  # 'libcamera', 'legacy', 'opencv', or 'mock'
        self.running = False
        self.frame = None
        self.frame_lock = threading.Lock()
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # Configuration
        self.width = CAMERA_CONFIG['width']
        self.height = CAMERA_CONFIG['height']
        self.fps_target = CAMERA_CONFIG['fps']
        self.rotation = CAMERA_CONFIG['rotation']
        
        # Initialize camera
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize camera with automatic fallback"""
        print("🎥 Initializing OV5647 camera...")
        
        # Try libcamera (modern)
        if PICAMERA2_AVAILABLE:
            if self._init_libcamera():
                return
        
        # Try legacy PiCamera
        if PICAMERA_LEGACY:
            if self._init_legacy():
                return
        
        # Try OpenCV
        if OPENCV_AVAILABLE:
            if self._init_opencv():
                return
        
        # Fallback to mock camera
        self._init_mock()
    
    def _init_libcamera(self) -> bool:
        """Initialize using libcamera (Picamera2)"""
        try:
            print("   Trying libcamera (Picamera2)...")
            self.camera = Picamera2()
            
            # Configure camera
            config = self.camera.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"}
            )
            self.camera.configure(config)
            
            # Start camera
            self.camera.start()
            
            # Warmup
            time.sleep(1)
            frame = self.camera.capture_array()
            if frame is not None:
                self.camera_type = 'libcamera'
                self.frame = frame
                print("   ✅ Libcamera initialized")
                return True
                
        except Exception as e:
            print(f"   ❌ Libcamera failed: {e}")
            self.camera = None
        
        return False
    
    def _init_legacy(self) -> bool:
        """Initialize using legacy PiCamera"""
        try:
            print("   Trying legacy PiCamera...")
            self.camera = PiCamera()
            
            # Configure camera
            self.camera.resolution = (self.width, self.height)
            self.camera.framerate = self.fps_target
            self.camera.rotation = self.rotation
            
            # Warmup
            time.sleep(2)
            
            self.camera_type = 'legacy'
            print("   ✅ Legacy PiCamera initialized")
            return True
            
        except Exception as e:
            print(f"   ❌ Legacy PiCamera failed: {e}")
            self.camera = None
        
        return False
    
    def _init_opencv(self) -> bool:
        """Initialize using OpenCV"""
        try:
            print("   Trying OpenCV...")
            for idx in [0, 1, 2]:
                try:
                    camera = cv2.VideoCapture(idx)
                    if camera.isOpened():
                        camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                        camera.set(cv2.CAP_PROP_FPS, self.fps_target)
                        
                        ret, frame = camera.read()
                        if ret and frame is not None:
                            self.camera = camera
                            self.camera_type = 'opencv'
                            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            print(f"   ✅ OpenCV initialized (index {idx})")
                            return True
                        else:
                            camera.release()
                except:
                    pass
            
        except Exception as e:
            print(f"   ❌ OpenCV failed: {e}")
        
        return False
    
    def _init_mock(self):
        """Initialize mock camera for testing"""
        print("   Using mock camera mode")
        self.camera_type = 'mock'
        self._generate_mock_frame()
    
    def _generate_mock_frame(self):
        """Generate mock frame for testing"""
        try:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            # Gradient background
            for i in range(self.height):
                frame[i, :] = [i//2, (i//3) % 255, (self.height-i)//2]
            
            # Add some shapes
            cv2.circle(frame, (160, 120), 50, (255, 255, 0), -1)
            cv2.rectangle(frame, (300, 200), (500, 350), (0, 255, 255), -1)
            
            # Add text
            cv2.putText(frame, "MOCK CAMERA", (150, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            
            ts = datetime.now().strftime("%H:%M:%S")
            cv2.putText(frame, f"Time: {ts}", (10, self.height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            with self.frame_lock:
                self.frame = frame
        
        except Exception as e:
            print(f"❌ Mock frame generation error: {e}")
    
    def start_capture(self):
        """Start camera capture thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print(f"✅ Camera capture started ({self.camera_type})")
    
    def stop_capture(self):
        """Stop camera capture"""
        print("🛑 Stopping camera capture...")
        self.running = False
        
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2)
        
        if self.camera:
            try:
                if self.camera_type == 'libcamera':
                    self.camera.stop()
                elif self.camera_type == 'legacy':
                    self.camera.close()
                elif self.camera_type == 'opencv':
                    self.camera.release()
            except:
                pass
        
        print("✅ Camera capture stopped")
    
    def _capture_loop(self):
        """Camera capture loop"""
        frame_count = 0
        last_time = time.time()
        
        while self.running:
            try:
                if self.camera_type == 'libcamera':
                    frame_array = self.camera.capture_array()
                    if frame_array is not None:
                        with self.frame_lock:
                            self.frame = frame_array
                        frame_count += 1
                
                elif self.camera_type == 'legacy':
                    output = io.BytesIO()
                    self.camera.capture(output, format='rgb')
                    output.seek(0)
                    frame_data = np.frombuffer(output.getvalue(), dtype=np.uint8)
                    frame = frame_data.reshape((self.height, self.width, 3))
                    with self.frame_lock:
                        self.frame = frame
                    frame_count += 1
                
                elif self.camera_type == 'opencv':
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        with self.frame_lock:
                            self.frame = frame_rgb
                        frame_count += 1
                
                elif self.camera_type == 'mock':
                    self._generate_mock_frame()
                    frame_count += 1
                
                # Update FPS
                current_time = time.time()
                if current_time - last_time >= 1.0:
                    self.fps = frame_count
                    frame_count = 0
                    last_time = current_time
                
                # Target FPS
                time.sleep(1.0 / self.fps_target)
                
            except Exception as e:
                print(f"❌ Capture error: {e}")
                time.sleep(0.1)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get latest frame"""
        with self.frame_lock:
            if self.frame is not None:
                return self.frame.copy()
        return None
    
    def save_frame(self, filename: str) -> bool:
        """Save current frame to file"""
        try:
            frame = self.get_frame()
            if frame is not None:
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, frame_bgr)
                return True
            return False
        except Exception as e:
            print(f"❌ Frame save error: {e}")
            return False
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.fps
    
    def is_active(self) -> bool:
        """Check if camera is active"""
        return self.camera is not None and self.frame is not None
    
    def get_camera_type(self) -> str:
        """Get camera type"""
        return self.camera_type or 'unknown'
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_capture()
        self.camera = None
        self.frame = None
        print("✅ Camera cleanup complete")