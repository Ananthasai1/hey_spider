"""
Utility Functions for Hey Spider Robot
Logging, performance tracking, and helper functions
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional


def timestamp() -> str:
    """
    Generate timestamp string for filenames
    
    Returns:
        Timestamp in format: YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def setup_logging(log_file: str = "logs/spider.log", 
                  level: str = "INFO",
                  max_bytes: int = 10485760,  # 10MB
                  backup_count: int = 5,
                  console_output: bool = True) -> logging.Logger:
    """
    Setup comprehensive logging configuration with rotation
    
    Args:
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    """
    # Create log directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('HeySpiderRobot')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File Handler with Rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Detailed format for file
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | '
        '%(filename)s:%(lineno)d | %(funcName)s() | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console Handler (if enabled)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Simpler format for console
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Error File Handler (separate file for errors)
    error_log_file = log_path.parent / f"{log_path.stem}_errors.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # Initial Log Entry
    logger.info("=" * 80)
    logger.info("🕷️  HEY SPIDER ROBOT - Logging Initialized")
    logger.info("=" * 80)
    logger.info(f"Log Level: {level}")
    logger.info(f"Log File: {log_file}")
    logger.info(f"Error Log: {error_log_file}")
    logger.info(f"Max Size: {max_bytes / 1024 / 1024:.1f} MB")
    logger.info(f"Backup Count: {backup_count}")
    logger.info(f"Console Output: {console_output}")
    logger.info("=" * 80)
    
    return logger


class PerformanceLogger:
    """Context manager for logging performance metrics"""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger('HeySpiderRobot')
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.debug(
                f"Completed: {self.operation_name} in {duration:.3f}s"
            )
        else:
            self.logger.error(
                f"Failed: {self.operation_name} after {duration:.3f}s - {exc_val}"
            )
        
        return False  # Don't suppress exceptions


def log_function_call(logger: Optional[logging.Logger] = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger('HeySpiderRobot')
            
            logger.debug(f"Calling: {func.__name__}()")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Success: {func.__name__}()")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}(): {e}")
                raise
        return wrapper
    return decorator


def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """Log exception with full traceback"""
    import traceback
    
    logger.error(f"Exception occurred: {context}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Exception message: {str(exc)}")
    logger.error("Traceback:")
    logger.error(traceback.format_exc())


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_size(bytes_size: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def map_range(value: float, 
              in_min: float, in_max: float,
              out_min: float, out_max: float) -> float:
    """
    Map value from one range to another
    
    Args:
        value: Input value
        in_min: Input range minimum
        in_max: Input range maximum
        out_min: Output range minimum
        out_max: Output range maximum
        
    Returns:
        Mapped value
    """
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# Example usage
if __name__ == "__main__":
    # Test logging
    logger = setup_logging("logs/test.log", level="DEBUG")
    logger.info("Testing logging system")
    
    # Test performance logger
    with PerformanceLogger("Test Operation", logger):
        time.sleep(0.5)
    
    # Test utilities
    print(f"Timestamp: {timestamp()}")
    print(f"Duration: {format_duration(3665)}")
    print(f"Size: {format_size(1536000)}")
    print(f"Clamp: {clamp(150, 0, 100)}")
    print(f"Map: {map_range(50, 0, 100, 0, 180)}")