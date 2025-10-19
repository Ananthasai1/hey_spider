# ============================================
# src/utils.py - CHANGE #6: Enhanced Logging Configuration
# Priority: 🟡 IMPORTANT
# Replace the existing setup_logging function (around line 13)
# ============================================

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path
from datetime import datetime


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
    
    # ============================================
    # File Handler with Rotation
    # ============================================
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
    
    # ============================================
    # Console Handler (if enabled)
    # ============================================
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Console shows INFO and above
        
        # Simpler format for console
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # ============================================
    # Error File Handler (separate file for errors)
    # ============================================
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
    
    # ============================================
    # Initial Log Entry
    # ============================================
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


# ============================================
# Additional Logging Utilities
# ============================================

class PerformanceLogger:
    """Context manager for logging performance metrics"""
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
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
                f"Completed: {self.operation_name} "
                f"in {duration:.3f}s"
            )
        else:
            self.logger.error(
                f"Failed: {self.operation_name} "
                f"after {duration:.3f}s - {exc_val}"
            )
        
        return False  # Don't suppress exceptions


def log_function_call(logger: logging.Logger = None):
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


# Example usage in main.py:
"""
from src.utils import setup_logging, PerformanceLogger, log_exception

def main():
    # Setup logging first
    logger = setup_logging(
        log_file=settings.get_log_path(),
        level=settings.LOG_LEVEL,
        console_output=True
    )
    
    logger.info("Starting Hey Spider Robot...")
    
    try:
        # Use performance logging
        with PerformanceLogger("Robot Initialization", logger):
            robot = HeySpiderRobot()
        
        # Start robot
        robot.start()
        
    except Exception as e:
        log_exception(logger, e, "Main robot startup")
        sys.exit(1)
"""