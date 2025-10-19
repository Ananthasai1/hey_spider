"""
Utility Functions
Helper functions for logging, timing, and data processing
"""

import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime(fmt)


def setup_logging(log_file: str = "logs/spider.log", level: str = "INFO"):
    """Setup logging configuration"""
    # Create log directory
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def save_json(data: Any, filepath: str) -> bool:
    """Save data to JSON file"""
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def load_json(filepath: str) -> Dict:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}


def frame_to_base64(frame) -> str:
    """Convert image frame to base64 string"""
    try:
        import cv2
        import base64
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode()
        return frame_base64
    except Exception as e:
        print(f"Frame encoding error: {e}")
        return ""


def get_file_size(filepath: str) -> str:
    """Get human-readable file size"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "Unknown"


def get_system_info() -> Dict:
    """Get system information"""
    import platform
    import sys
    
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
    except ImportError:
        cpu_percent = 0
        memory = None
    
    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'cpu_percent': cpu_percent,
    }
    
    if memory:
        info['memory'] = {
            'total': f"{memory.total / 1024**3:.1f} GB",
            'used': f"{memory.used / 1024**3:.1f} GB",
            'percent': memory.percent
        }
    
    return info


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


class Timer:
    """Simple timing context manager"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        print(f"Timer {self.name}: {self.elapsed:.3f}s")


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics = {}
    
    def record(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(value)
        
        if len(self.metrics[metric_name]) > self.window_size:
            self.metrics[metric_name].pop(0)
    
    def get_average(self, metric_name: str) -> float:
        """Get average of metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0.0
        
        values = self.metrics[metric_name]
        return sum(values) / len(values)
    
    def get_max(self, metric_name: str) -> float:
        """Get max of metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0.0
        
        return max(self.metrics[metric_name])
    
    def get_min(self, metric_name: str) -> float:
        """Get min of metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0.0
        
        return min(self.metrics[metric_name])
    
    def get_stats(self) -> Dict:
        """Get all statistics"""
        stats = {}
        for metric_name in self.metrics.keys():
            stats[metric_name] = {
                'avg': self.get_average(metric_name),
                'max': self.get_max(metric_name),
                'min': self.get_min(metric_name),
                'count': len(self.metrics[metric_name])
            }
        return stats


def ensure_directories(*dirs: str):
    """Ensure directories exist"""
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)