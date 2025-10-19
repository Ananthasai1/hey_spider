"""
Standard Visual Monitor - YOLO v8 Object Detection
Lightweight version for systems without advanced camera features
"""

import threading
import time
import os
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("Warning: OpenCV not available - camera disabled")
    OPENCV_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    print("Warning: YOLO not available - object detection disabled")
    YOLO_AVAILABLE = False

from config.yolo_detection_config import YOLOConfig, ENHANCED_CLASS_INFO
from src.oled_display import OLEDDisplay
from src.utils import timestamp


class VisualMonitor:
    """Visual monitoring with YOLO v8 detection"""
    
    def __init__(self, oled_display: Optional[OLEDDisplay] = None):
        self.oled = oled_display
        self.camera = None
        self.model = None
        self.running = False
        self.camera_active = False
        
        # Threads
        self.capture_thread = None
        self.detection_thread = None
        
        # Detection data
        self.latest_detections = []
        self.latest_frame = None
        self.annotated_frame = None
        self.detection_history = []
        
        # Performance
        self.current_fps = 0
        self.detection_times = []
        
        # Configuration
        self.config = YOLOConfig()
        
        # Create directories
        os.makedirs('images', exist_ok=True)
        os.makedirs('images/detections', exist_ok=True)
        os.makedirs('images/raw', exist_ok=True)
        
        # Initialize
        self._initialize_yolo()
        self._initialize_camera()
        
    def _initialize_yolo(self):
        """Initialize YOLO model"""
        if not YOLO_AVAILABLE:
            print("Warning: YOLO not available - using mock detection")
            return
            
        try:
            model_paths = [
                self.config.MODEL_PATH,
                'yolov8n.pt',
                'models/yolov8n.pt',
            ]
            
            for model_path in model_paths:
                try:
                    print(f"Loading YOLO model: {model_path}")
                    self.model = YOLO(model_path)
                    
                    # Test model
                    test_img = np.zeros((640, 640, 3), dtype=np.uint8)
                    _ = self.model(test_img, verbose=False)
                    
                    print(f"YOLO model loaded: {model_path}")
                    print(f"   Classes: {len(self.model.names)}")
                    return
                    
                except Exception as e:
                    print(f"   Failed to load {model_path}: {e}")
                    continue
                    
            print("Warning: All YOLO models failed - using mock detection")
            self.model = None
            
        except Exception as e:
            print(f"Error: YOLO initialization failed: {e}")
            self.model = None
    
    def _initialize_camera(self):
        """Initialize camera"""
        if self.camera_active:
            return True
            
        if not OPENCV_AVAILABLE:
            print("Warning: OpenCV not available - using mock camera")
            self.camera_active = True
            self._generate_mock_frame()
            return True
            
        try:
            # Try different camera indices
            for idx in [0, 1, 2]:
                try:
                    print(f"Trying camera index: {idx}")
                    self.camera = cv2.VideoCapture(idx)
                    
                    if self.camera.isOpened():
                        # Configure camera
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.camera.set(cv2.CAP_PROP_FPS, 30)
                        
                        # Test capture
                        ret, frame = self.camera.read()
                        if ret and frame is not None:
                            self.latest_frame = frame
                            self.annotated_frame = frame.copy()
                            self.camera_active = True
                            print(f"Camera initialized: {frame.shape}")
                            return True
                        else:
                            self.camera.release()
                            
                except Exception as e:
                    print(f"   Camera {idx} failed: {e}")
                    if self.camera:
                        self.camera.release()
                        self.camera = None
                    
            print("Warning: No camera found - using mock mode")
            self.camera_active = True
            self._generate_mock_frame()
            return False
            
        except Exception as e:
            print(f"Error: Camera initialization failed: {e}")
            self.camera_active = True
            self._generate_mock_frame()
            return False
    
    def start_monitoring(self):
        """Start visual monitoring"""
        if self.running:
            return
            
        self.running = True
        
        # Start capture thread
        self.capture_thread = threading.Thread(
            target=self._capture_loop, 
            daemon=True
        )
        self.capture_thread.start()
        
        # Start detection thread
        self.detection_thread = threading.Thread(
            target=self._detection_loop, 
            daemon=True
        )
        self.detection_thread.start()
        
        print("Visual monitoring started")
    
    def stop_monitoring(self):
        """Stop visual monitoring"""
        print("Stopping visual monitoring...")
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.detection_thread:
            self.detection_thread.join(timeout=2)
            
        if self.camera and self.camera.isOpened():
            self.camera.release()
            
        print("Visual monitoring stopped")
    
    def _capture_loop(self):
        """Camera capture loop"""
        frame_count = 0
        last_fps_time = time.time()
        
        while self.running:
            try:
                if self.camera and self.camera.isOpened():
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        self.latest_frame = frame.copy()
                        frame_count += 1
                        
                        # Update FPS
                        current_time = time.time()
                        if current_time - last_fps_time >= 1.0:
                            self.current_fps = frame_count
                            frame_count = 0
                            last_fps_time = current_time
                    else:
                        time.sleep(0.1)
                else:
                    # Generate mock frame
                    if frame_count % 30 == 0:
                        self._generate_mock_frame()
                    frame_count += 1
                    
                time.sleep(1/30)  # 30 FPS target
                
            except Exception as e:
                print(f"Error: Capture error: {e}")
                time.sleep(1)
    
    def _detection_loop(self):
        """Object detection loop"""
        last_detection = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time - last_detection >= self.config.DETECTION_INTERVAL:
                    if self.latest_frame is not None:
                        self._process_detection(self.latest_frame)
                        last_detection = current_time
                        
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Error: Detection error: {e}")
                time.sleep(0.5)
    
    def _process_detection(self, frame):
        """Process frame for object detection"""
        if not self.model:
            self._generate_mock_detections()
            return
            
        try:
            start_time = time.time()
            
            # Run YOLO detection
            results = self.model(
                frame,
                conf=self.config.CONFIDENCE_THRESHOLD,
                iou=self.config.IOU_THRESHOLD,
                max_det=self.config.MAX_DETECTIONS,
                verbose=False
            )
            
            detections = []
            annotated_frame = frame.copy()
            
            # Process results
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for i in range(len(result.boxes)):
                        box = result.boxes.xyxy[i].cpu().numpy()
                        conf = float(result.boxes.conf[i].cpu().numpy())
                        cls = int(result.boxes.cls[i].cpu().numpy())
                        
                        if conf >= self.config.CONFIDENCE_THRESHOLD:
                            class_name = self.model.names.get(cls, f"class_{cls}")
                            
                            detection = {
                                'class': class_name,
                                'confidence': conf,
                                'bbox': box.tolist(),
                                'class_id': cls,
                                'timestamp': time.time()
                            }
                            detections.append(detection)
                            
                            # Draw on frame
                            x1, y1, x2, y2 = map(int, box)
                            color = self._get_class_color(cls)
                            
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                            
                            label = f"{class_name}: {conf:.2f}"
                            cv2.putText(
                                annotated_frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                            )
            
            self.latest_detections = detections
            self.annotated_frame = annotated_frame
            
            # Performance tracking
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            if len(self.detection_times) > 100:
                self.detection_times.pop(0)
            
            # Update OLED
            if self.oled:
                self.oled.update_detections(detections)
                
        except Exception as e:
            print(f"Error: Detection processing failed: {e}")
            self._generate_mock_detections()
    
    def _get_class_color(self, class_id: int) -> Tuple[int, int, int]:
        """Get color for object class"""
        if class_id in ENHANCED_CLASS_INFO:
            return ENHANCED_CLASS_INFO[class_id]['color']
        
        # Generate consistent color
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))
    
    def _generate_mock_frame(self):
        """Generate mock camera frame"""
        try:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Gradient background
            for i in range(480):
                frame[i, :] = [i//2, (i//3) % 255, (480-i)//2]
            
            # Add shapes
            cv2.circle(frame, (160, 120), 50, (255, 255, 0), -1)
            cv2.rectangle(frame, (300, 200), (500, 350), (0, 255, 255), -1)
            
            # Add text
            cv2.putText(
                frame, "MOCK CAMERA",
                (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 255, 255), 2
            )
            
            ts = datetime.now().strftime("%H:%M:%S")
            cv2.putText(
                frame, f"Time: {ts}",
                (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255, 255, 255), 2
            )
            
            self.latest_frame = frame
            self.annotated_frame = frame.copy()
            
        except Exception as e:
            print(f"Error: Mock frame generation failed: {e}")
    
    def _generate_mock_detections(self):
        """Generate mock detections for testing"""
        import random
        
        mock_objects = [
            ('person', 0.85),
            ('chair', 0.78),
            ('laptop', 0.72),
            ('cup', 0.65),
            ('book', 0.70),
        ]
        
        num_detections = random.randint(0, 3)
        detections = []
        
        if self.latest_frame is not None:
            h, w = self.latest_frame.shape[:2]
        else:
            w, h = 640, 480
        
        for _ in range(num_detections):
            obj_class, confidence = random.choice(mock_objects)
            
            x1 = random.randint(50, w - 200)
            y1 = random.randint(50, h - 150)
            x2 = min(x1 + random.randint(80, 200), w - 10)
            y2 = min(y1 + random.randint(60, 150), h - 10)
            
            detections.append({
                'class': obj_class,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2],
                'class_id': random.randint(0, 79),
                'timestamp': time.time()
            })
        
        self.latest_detections = detections
        
        if self.oled:
            self.oled.update_detections(detections)
    
    def capture_photo(self) -> str:
        """Capture and save photo"""
        try:
            frame = self.annotated_frame if self.annotated_frame is not None else self.latest_frame
            
            if frame is not None:
                ts = timestamp()
                
                # Save raw frame
                raw_file = f"images/raw/photo_{ts}.jpg"
                cv2.imwrite(raw_file, self.latest_frame if self.latest_frame is not None else frame)
                
                # Save annotated frame
                annotated_file = f"images/detections/photo_{ts}_detected.jpg"
                
                # Add info overlay
                if self.latest_detections:
                    info = f"Detections: {len(self.latest_detections)} | FPS: {self.current_fps}"
                    cv2.putText(
                        frame, info, (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                    )
                
                cv2.imwrite(annotated_file, frame)
                print(f"Photo saved: {annotated_file}")
                return annotated_file
            else:
                print("Error: No frame available")
                return ""
                
        except Exception as e:
            print(f"Error: Photo capture failed: {e}")
            return ""
    
    def get_latest_detections(self) -> List[Dict]:
        """Get latest detections"""
        return self.latest_detections.copy()
    
    def get_detection_description(self) -> str:
        """Get natural language description of detections"""
        if not self.latest_detections:
            return "No objects detected in view"
        
        # Count objects
        counts = {}
        for det in self.latest_detections:
            cls = det['class']
            counts[cls] = counts.get(cls, 0) + 1
        
        # Build description
        descriptions = []
        for cls, count in counts.items():
            if count == 1:
                descriptions.append(f"1 {cls}")
            else:
                descriptions.append(f"{count} {cls}s")
        
        if len(descriptions) == 0:
            return "No objects detected"
        elif len(descriptions) == 1:
            return f"I can see {descriptions[0]}."
        elif len(descriptions) == 2:
            return f"I can see {descriptions[0]} and {descriptions[1]}."
        else:
            return f"I can see {', '.join(descriptions[:-1])}, and {descriptions[-1]}."
    
    def get_latest_frame(self):
        """Get latest raw frame"""
        return self.latest_frame
    
    def get_annotated_frame(self):
        """Get annotated frame with detections"""
        return self.annotated_frame if self.annotated_frame is not None else self.latest_frame
    
    def is_camera_active(self) -> bool:
        """Check if camera is active"""
        return self.camera_active
    
    def get_detection_stats(self) -> Dict:
        """Get detection statistics"""
        avg_time = 0
        if self.detection_times:
            avg_time = sum(self.detection_times) / len(self.detection_times)
        
        return {
            'fps': self.current_fps,
            'avg_detection_time': avg_time,
            'current_objects': len(self.latest_detections),
            'model_loaded': self.model is not None,
            'camera_active': self.camera_active,
        }
    
    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up visual monitor...")
        self.stop_monitoring()
        
        if self.camera and self.camera.isOpened():
            self.camera.release()
        
        self.latest_detections.clear()
        self.detection_history.clear()
        
        print("Visual monitor cleanup complete")