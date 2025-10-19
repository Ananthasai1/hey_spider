"""
YOLO Detection Configuration
Object detection parameters and class information
"""

from pathlib import Path
from typing import Dict, Tuple

# ============================================
# YOLO Model Configuration
# ============================================
class YOLOConfig:
    """YOLO detection configuration"""
    
    # Model paths
    MODEL_PATH = "yolov8n.pt"  # Nano model (fastest, smallest)
    # Alternatives:
    # "yolov8s.pt"  - Small model
    # "yolov8m.pt"  - Medium model
    # "yolov8l.pt"  - Large model
    # "yolo12n.pt"  - YOLOv12 Nano (if available)
    
    # Detection parameters
    CONFIDENCE_THRESHOLD = 0.5   # 50% confidence minimum
    IOU_THRESHOLD = 0.4          # IoU threshold for NMS
    MAX_DETECTIONS = 20          # Maximum objects per frame
    DETECTION_INTERVAL = 0.1     # Seconds between detections
    
    # Performance
    DEVICE = 'auto'              # auto, cpu, cuda, 0, 1, 2 ...
    FP16 = False                 # Use half precision
    MAX_DET = 20                 # Max detections per image
    
    # Input
    IMGSZ = 640                  # Image size for inference
    
    # Output
    SAVE_DETECTIONS = True
    SAVE_CONFIDENCE = True


# ============================================
# COCO Classes (YOLOv8 Standard)
# ============================================
COCO_CLASSES = {
    0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
    5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
    10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
    14: 'cat', 15: 'dog', 16: 'horse', 17: 'sheep', 18: 'cow', 19: 'elephant',
    20: 'bear', 21: 'zebra', 22: 'giraffe', 23: 'backpack', 24: 'umbrella',
    25: 'handbag', 26: 'tie', 27: 'suitcase', 28: 'frisbee', 29: 'skis',
    30: 'snowboard', 31: 'sports ball', 32: 'kite', 33: 'baseball bat',
    34: 'baseball glove', 35: 'skateboard', 36: 'surfboard', 37: 'tennis racket',
    38: 'bottle', 39: 'wine glass', 40: 'cup', 41: 'fork', 42: 'knife',
    43: 'spoon', 44: 'bowl', 45: 'banana', 46: 'apple', 47: 'sandwich',
    48: 'orange', 49: 'broccoli', 50: 'carrot', 51: 'hot dog', 52: 'pizza',
    53: 'donut', 54: 'cake', 55: 'chair', 56: 'couch', 57: 'potted plant',
    58: 'bed', 59: 'dining table', 60: 'toilet', 61: 'tv', 62: 'laptop',
    63: 'mouse', 64: 'remote', 65: 'keyboard', 66: 'microwave', 67: 'oven',
    68: 'toaster', 69: 'sink', 70: 'refrigerator', 71: 'book', 72: 'clock',
    73: 'vase', 74: 'scissors', 75: 'teddy bear', 76: 'hair drier',
    77: 'toothbrush'
}

# ============================================
# Enhanced Class Information
# ============================================
ENHANCED_CLASS_INFO = {
    # Format: class_id: {'name': str, 'color': (B, G, R), 'category': str}
    
    # People
    0: {'name': 'person', 'color': (0, 255, 0), 'category': 'human'},
    
    # Animals
    14: {'name': 'cat', 'color': (255, 165, 0), 'category': 'animal'},
    15: {'name': 'dog', 'color': (255, 165, 0), 'category': 'animal'},
    16: {'name': 'horse', 'color': (255, 165, 0), 'category': 'animal'},
    17: {'name': 'sheep', 'color': (255, 165, 0), 'category': 'animal'},
    18: {'name': 'cow', 'color': (255, 165, 0), 'category': 'animal'},
    
    # Vehicles
    2: {'name': 'car', 'color': (0, 0, 255), 'category': 'vehicle'},
    3: {'name': 'motorcycle', 'color': (0, 0, 255), 'category': 'vehicle'},
    5: {'name': 'bus', 'color': (0, 0, 255), 'category': 'vehicle'},
    6: {'name': 'train', 'color': (0, 0, 255), 'category': 'vehicle'},
    7: {'name': 'truck', 'color': (0, 0, 255), 'category': 'vehicle'},
    
    # Electronics
    61: {'name': 'tv', 'color': (255, 0, 255), 'category': 'electronics'},
    62: {'name': 'laptop', 'color': (255, 0, 255), 'category': 'electronics'},
    63: {'name': 'mouse', 'color': (255, 0, 255), 'category': 'electronics'},
    65: {'name': 'keyboard', 'color': (255, 0, 255), 'category': 'electronics'},
    
    # Food
    45: {'name': 'banana', 'color': (0, 255, 255), 'category': 'food'},
    46: {'name': 'apple', 'color': (0, 255, 255), 'category': 'food'},
    47: {'name': 'sandwich', 'color': (0, 255, 255), 'category': 'food'},
    48: {'name': 'orange', 'color': (0, 255, 255), 'category': 'food'},
    
    # Common Objects
    38: {'name': 'bottle', 'color': (128, 0, 128), 'category': 'object'},
    40: {'name': 'cup', 'color': (128, 0, 128), 'category': 'object'},
    44: {'name': 'bowl', 'color': (128, 0, 128), 'category': 'object'},
    71: {'name': 'book', 'color': (128, 0, 128), 'category': 'object'},
}

# ============================================
# Color Palette for Visualization
# ============================================
COLOR_MAP = {
    'person': (0, 255, 0),           # Green
    'animal': (255, 165, 0),         # Orange
    'vehicle': (0, 0, 255),          # Red
    'electronics': (255, 0, 255),    # Magenta
    'food': (0, 255, 255),           # Yellow
    'object': (128, 0, 128),         # Purple
    'other': (192, 192, 192),        # Gray
}

# ============================================
# Detection Filtering
# ============================================
class DetectionFilter:
    """Filter detections based on criteria"""
    
    # Classes to ignore
    IGNORE_CLASSES = {
        11: 'stop sign',  # Too common
        12: 'parking meter',  # Not relevant
    }
    
    # Minimum confidence by class
    MIN_CONFIDENCE_BY_CLASS = {
        0: 0.6,   # person (higher threshold)
        14: 0.5,  # cat
        15: 0.5,  # dog
    }
    
    @staticmethod
    def should_include(class_id: int, confidence: float) -> bool:
        """Check if detection should be included"""
        if class_id in DetectionFilter.IGNORE_CLASSES:
            return False
        
        min_conf = DetectionFilter.MIN_CONFIDENCE_BY_CLASS.get(
            class_id, YOLOConfig.CONFIDENCE_THRESHOLD
        )
        
        return confidence >= min_conf


# ============================================
# Performance Optimization
# ============================================
class PerformanceConfig:
    """Performance tuning options"""
    
    # Frame skipping for faster processing
    SKIP_FRAMES = 2  # Process every Nth frame
    
    # Resize frames for faster detection
    RESIZE_FACTOR = 1.0  # 1.0 = full size, 0.5 = half size
    
    # Use lower resolution model
    USE_NANO_MODEL = True  # Use yolov8n instead of yolov8m
    
    # Threading
    USE_THREADING = True
    NUM_THREADS = 4
    
    # Cache detections
    CACHE_DETECTIONS = True
    CACHE_TTL = 0.1  # seconds


# ============================================
# Utilities
# ============================================
def get_class_name(class_id: int) -> str:
    """Get class name by ID"""
    return COCO_CLASSES.get(class_id, f'class_{class_id}')


def get_class_color(class_id: int) -> Tuple[int, int, int]:
    """Get color for class ID"""
    if class_id in ENHANCED_CLASS_INFO:
        return ENHANCED_CLASS_INFO[class_id]['color']
    
    # Generate consistent color from class ID
    import hashlib
    hash_obj = hashlib.md5(str(class_id).encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    b = (hash_int >> 0) & 0xFF
    g = (hash_int >> 8) & 0xFF
    r = (hash_int >> 16) & 0xFF
    
    return (b, g, r)


def get_category(class_id: int) -> str:
    """Get category for class ID"""
    if class_id in ENHANCED_CLASS_INFO:
        return ENHANCED_CLASS_INFO[class_id]['category']
    return 'other'


if __name__ == "__main__":
    config = YOLOConfig()
    print(f"YOLO Config: {config.MODEL_PATH}")
    print(f"Confidence threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"Total COCO classes: {len(COCO_CLASSES)}")
    print(f"Enhanced classes: {len(ENHANCED_CLASS_INFO)}")