# ============================================
# src/performance_monitor.py - CHANGE #8: Add Performance Monitoring
# Priority: 🟡 IMPORTANT
# NEW FILE - Create this file
# ============================================

"""
Performance Monitor
Track system metrics and performance for Hey Spider Robot
"""

import time
import threading
from collections import deque
from typing import Dict, Optional, List
from datetime import datetime


try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("⚠️  psutil not available - system metrics limited")
    PSUTIL_AVAILABLE = False


class PerformanceMonitor:
    """Monitor system and application performance"""
    
    def __init__(self, window_size: int = 100):
        """
        Initialize performance monitor
        
        Args:
            window_size: Number of samples to keep for rolling averages
        """
        self.window_size = window_size
        self.running = False
        self.thread = None
        
        # Metric storage
        self.metrics = {
            'fps': deque(maxlen=window_size),
            'cpu': deque(maxlen=window_size),
            'memory': deque(maxlen=window_size),
            'temperature': deque(maxlen=window_size),
            'detection_time': deque(maxlen=window_size),
            'frame_latency': deque(maxlen=window_size),
        }
        
        # Alert thresholds
        self.thresholds = {
            'cpu_warning': 80,
            'cpu_critical': 90,
            'memory_warning': 85,
            'memory_critical': 95,
            'temp_warning': 70,
            'temp_critical': 80,
            'fps_warning': 10,
            'fps_critical': 5,
        }
        
        # Statistics
        self.start_time = time.time()
        self.sample_count = 0
    
    def start(self):
        """Start monitoring in background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("✅ Performance monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        print("🛑 Stopping performance monitoring...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        print("✅ Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._collect_system_metrics()
                self.sample_count += 1
                time.sleep(1)  # Sample every second
            except Exception as e:
                print(f"❌ Performance monitoring error: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # CPU usage
            cpu = psutil.cpu_percent(interval=0.1)
            self.metrics['cpu'].append(cpu)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory'].append(memory.percent)
            
            # Temperature (Raspberry Pi specific)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read()) / 1000.0
                    self.metrics['temperature'].append(temp)
            except:
                pass  # Not on Raspberry Pi or no temp sensor
                
        except Exception as e:
            print(f"❌ Error collecting system metrics: {e}")
    
    def record_fps(self, fps: float):
        """Record FPS metric"""
        self.metrics['fps'].append(fps)
    
    def record_detection_time(self, time_ms: float):
        """Record detection time in milliseconds"""
        self.metrics['detection_time'].append(time_ms)
    
    def record_frame_latency(self, latency_ms: float):
        """Record frame capture latency in milliseconds"""
        self.metrics['frame_latency'].append(latency_ms)
    
    def get_stats(self) -> Dict:
        """
        Get current statistics for all metrics
        
        Returns:
            Dictionary with current, avg, min, max for each metric
        """
        stats = {}
        
        for key, values in self.metrics.items():
            if values:
                stats[key] = {
                    'current': values[-1],
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'samples': len(values)
                }
            else:
                stats[key] = {
                    'current': 0,
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'samples': 0
                }
        
        # Add uptime
        stats['uptime'] = time.time() - self.start_time
        stats['sample_count'] = self.sample_count
        
        return stats
    
    def get_alerts(self) -> List[Dict]:
        """
        Get performance alerts based on thresholds
        
        Returns:
            List of alert dictionaries with level, metric, and message
        """
        alerts = []
        stats = self.get_stats()
        
        # CPU alerts
        if 'cpu' in stats and stats['cpu']['samples'] > 0:
            cpu_avg = stats['cpu']['avg']
            if cpu_avg >= self.thresholds['cpu_critical']:
                alerts.append({
                    'level': 'critical',
                    'metric': 'cpu',
                    'message': f"Critical CPU usage: {cpu_avg:.1f}%",
                    'value': cpu_avg
                })
            elif cpu_avg >= self.thresholds['cpu_warning']:
                alerts.append({
                    'level': 'warning',
                    'metric': 'cpu',
                    'message': f"High CPU usage: {cpu_avg:.1f}%",
                    'value': cpu_avg
                })
        
        # Memory alerts
        if 'memory' in stats and stats['memory']['samples'] > 0:
            mem_avg = stats['memory']['avg']
            if mem_avg >= self.thresholds['memory_critical']:
                alerts.append({
                    'level': 'critical',
                    'metric': 'memory',
                    'message': f"Critical memory usage: {mem_avg:.1f}%",
                    'value': mem_avg
                })
            elif mem_avg >= self.thresholds['memory_warning']:
                alerts.append({
                    'level': 'warning',
                    'metric': 'memory',
                    'message': f"High memory usage: {mem_avg:.1f}%",
                    'value': mem_avg
                })
        
        # Temperature alerts
        if 'temperature' in stats and stats['temperature']['samples'] > 0:
            temp_current = stats['temperature']['current']
            if temp_current >= self.thresholds['temp_critical']:
                alerts.append({
                    'level': 'critical',
                    'metric': 'temperature',
                    'message': f"Critical temperature: {temp_current:.1f}°C",
                    'value': temp_current
                })
            elif temp_current >= self.thresholds['temp_warning']:
                alerts.append({
                    'level': 'warning',
                    'metric': 'temperature',
                    'message': f"Elevated temperature: {temp_current:.1f}°C",
                    'value': temp_current
                })
        
        # FPS alerts
        if 'fps' in stats and stats['fps']['samples'] > 0:
            fps_avg = stats['fps']['avg']
            if fps_avg <= self.thresholds['fps_critical']:
                alerts.append({
                    'level': 'critical',
                    'metric': 'fps',
                    'message': f"Critical low FPS: {fps_avg:.1f}",
                    'value': fps_avg
                })
            elif fps_avg <= self.thresholds['fps_warning']:
                alerts.append({
                    'level': 'warning',
                    'metric': 'fps',
                    'message': f"Low FPS: {fps_avg:.1f}",
                    'value': fps_avg
                })
        
        return alerts
    
    def get_summary(self) -> str:
        """
        Get human-readable performance summary
        
        Returns:
            Formatted string with performance summary
        """
        stats = self.get_stats()
        alerts = self.get_alerts()
        
        lines = [
            "=" * 60,
            "📊 PERFORMANCE SUMMARY",
            "=" * 60,
        ]
        
        # Uptime
        uptime = stats.get('uptime', 0)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        lines.append(f"⏱️  Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        lines.append(f"📝 Samples: {stats.get('sample_count', 0)}")
        lines.append("")
        
        # System metrics
        if PSUTIL_AVAILABLE:
            lines.append("🖥️  System Metrics:")
            
            if 'cpu' in stats and stats['cpu']['samples'] > 0:
                cpu = stats['cpu']
                lines.append(f"   CPU: {cpu['current']:.1f}% "
                           f"(avg: {cpu['avg']:.1f}%, max: {cpu['max']:.1f}%)")
            
            if 'memory' in stats and stats['memory']['samples'] > 0:
                mem = stats['memory']
                lines.append(f"   Memory: {mem['current']:.1f}% "
                           f"(avg: {mem['avg']:.1f}%, max: {mem['max']:.1f}%)")
            
            if 'temperature' in stats and stats['temperature']['samples'] > 0:
                temp = stats['temperature']
                lines.append(f"   Temp: {temp['current']:.1f}°C "
                           f"(avg: {temp['avg']:.1f}°C, max: {temp['max']:.1f}°C)")
            lines.append("")
        
        # Vision metrics
        if 'fps' in stats and stats['fps']['samples'] > 0:
            lines.append("🎥 Vision Metrics:")
            
            fps = stats['fps']
            lines.append(f"   FPS: {fps['current']:.1f} "
                        f"(avg: {fps['avg']:.1f}, min: {fps['min']:.1f})")
            
            if 'detection_time' in stats and stats['detection_time']['samples'] > 0:
                det = stats['detection_time']
                lines.append(f"   Detection: {det['current']:.1f}ms "
                           f"(avg: {det['avg']:.1f}ms)")
            
            if 'frame_latency' in stats and stats['frame_latency']['samples'] > 0:
                lat = stats['frame_latency']
                lines.append(f"   Latency: {lat['current']:.1f}ms "
                           f"(avg: {lat['avg']:.1f}ms)")
            lines.append("")
        
        # Alerts
        if alerts:
            lines.append("⚠️  Active Alerts:")
            for alert in alerts:
                emoji = "🔴" if alert['level'] == 'critical' else "🟡"
                lines.append(f"   {emoji} {alert['message']}")
            lines.append("")
        else:
            lines.append("✅ No performance alerts")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def print_summary(self):
        """Print performance summary to console"""
        print(self.get_summary())
    
    def export_to_dict(self) -> Dict:
        """
        Export all performance data to dictionary
        
        Returns:
            Complete performance data dictionary
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - self.start_time,
            'sample_count': self.sample_count,
            'stats': self.get_stats(),
            'alerts': self.get_alerts(),
            'thresholds': self.thresholds
        }
    
    def save_to_file(self, filename: str = "data/performance_log.json"):
        """
        Save performance data to JSON file
        
        Args:
            filename: Path to save file
        """
        import json
        from pathlib import Path
        
        try:
            # Create directory if needed
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Export data
            data = self.export_to_dict()
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Performance data saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving performance data: {e}")
    
    def set_threshold(self, metric: str, level: str, value: float):
        """
        Set custom threshold value
        
        Args:
            metric: Metric name (cpu, memory, temperature, fps)
            level: Alert level (warning, critical)
            value: Threshold value
        """
        key = f"{metric}_{level}"
        if key in self.thresholds:
            self.thresholds[key] = value
            print(f"✅ Threshold updated: {key} = {value}")
        else:
            print(f"❌ Unknown threshold: {key}")
    
    def reset_metrics(self):
        """Clear all collected metrics"""
        for key in self.metrics:
            self.metrics[key].clear()
        
        self.sample_count = 0
        self.start_time = time.time()
        print("✅ Metrics reset")


# ============================================
# Usage Example in main.py
# ============================================

"""
from src.performance_monitor import PerformanceMonitor

class HeySpiderRobot:
    def __init__(self):
        # ... existing code ...
        
        # Add performance monitor
        self.perf_monitor = PerformanceMonitor(window_size=100)
        
    def start(self):
        # ... existing code ...
        
        # Start performance monitoring
        if settings.ENABLE_PERFORMANCE_TRACKING:
            self.perf_monitor.start()
        
    def stop(self):
        # ... existing code ...
        
        # Print performance summary
        if self.perf_monitor:
            self.perf_monitor.print_summary()
            self.perf_monitor.save_to_file()
            self.perf_monitor.stop()

# In vision monitor, record FPS:
if self.perf_monitor:
    self.perf_monitor.record_fps(self.current_fps)
    self.perf_monitor.record_detection_time(detection_time * 1000)
"""