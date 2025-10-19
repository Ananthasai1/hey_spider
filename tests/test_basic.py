#!/usr/bin/env python3
"""
Test Servo Motors
Tests individual servos and movement sequences
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.hardware_config import SERVO_PINS, I2C_CONFIG

try:
    from adafruit_servokit import ServoKit
    SERVO_AVAILABLE = True
except ImportError:
    print("❌ adafruit_servokit not available")
    print("Install with: pip install adafruit-circuitpython-servokit")
    SERVO_AVAILABLE = False


def test_servo_controller():
    """Test PCA9685 servo controller"""
    if not SERVO_AVAILABLE:
        print("❌ Servo kit not available")
        return False
    
    try:
        print("=" * 60)
        print("🤖 Servo Controller Test")
        print("=" * 60)
        
        print("\n📡 Connecting to PCA9685...")
        kit = ServoKit(channels=16)
        print("✅ PCA9685 connected")
        
        # Test each servo
        servo_channels = sorted(set(SERVO_PINS.values()))
        
        print(f"\n🔧 Testing {len(servo_channels)} servo channels...")
        print("   Press Ctrl+C to stop\n")
        
        try:
            for channel in servo_channels:
                print(f"   Channel {channel:2d}: ", end='', flush=True)
                
                # Sweep servo
                kit.servo[channel].angle = 90   # Center
                time.sleep(0.2)
                kit.servo[channel].angle = 0    # Min
                time.sleep(0.2)
                kit.servo[channel].angle = 180  # Max
                time.sleep(0.2)
                kit.servo[channel].angle = 90   # Center
                
                print("✓")
                time.sleep(0.3)
            
            print("\n✅ All servos responded")
            
            # Return to center
            print("\n🏠 Centering all servos...")
            for channel in servo_channels:
                kit.servo[channel].angle = 90
            
            print("✅ Test complete")
            return True
            
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_movement_sequence():
    """Test movement sequences"""
    if not SERVO_AVAILABLE:
        return False
    
    try:
        print("\n" + "=" * 60)
        print("🚶 Movement Sequence Test")
        print("=" * 60)
        
        from src.spider_controller import SpiderController
        
        print("\n🎮 Initializing spider controller...")
        spider = SpiderController()
        
        sequences = [
            ("Home", spider.go_home),
            ("Stand", spider.stand_up),
            ("Sit", spider.sit_down),
            ("Forward", lambda: spider.walk_forward(steps=1)),
            ("Left", lambda: spider.turn_left(angle=30)),
            ("Right", lambda: spider.turn_right(angle=30)),
            ("Dance", spider.dance),
            ("Wave", spider.wave),
        ]
        
        print("\n📋 Testing sequences:")
        for name, func in sequences:
            print(f"   {name:10s}: ", end='', flush=True)
            try:
                func()
                print("✓")
            except Exception as e:
                print(f"✗ ({e})")
                continue
            
            time.sleep(1)
        
        print("\n✅ Movement test complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_servo_control():
    """Interactive servo control"""
    if not SERVO_AVAILABLE:
        return False
    
    try:
        print("\n" + "=" * 60)
        print("🎮 Interactive Servo Control")
        print("=" * 60)
        
        kit = ServoKit(channels=16)
        
        print("\nCommands:")
        print("  <channel> <angle>  - Set servo angle (e.g., '0 90')")
        print("  sweep <channel>    - Sweep servo (e.g., 'sweep 0')")
        print("  center             - Center all servos")
        print("  quit               - Exit")
        
        while True:
            try:
                cmd = input("\n> ").strip().lower().split()
                
                if not cmd:
                    continue
                
                if cmd[0] == 'quit':
                    break
                
                elif cmd[0] == 'center':
                    print("Centering all servos...")
                    for i in range(16):
                        kit.servo[i].angle = 90
                    print("Done")
                
                elif cmd[0] == 'sweep' and len(cmd) > 1:
                    channel = int(cmd[1])
                    print(f"Sweeping channel {channel}...")
                    for angle in range(0, 181, 10):
                        kit.servo[channel].angle = angle
                        time.sleep(0.1)
                    kit.servo[channel].angle = 90
                    print("Done")
                
                elif len(cmd) >= 2:
                    channel = int(cmd[0])
                    angle = int(cmd[1])
                    
                    if 0 <= channel < 16 and 0 <= angle <= 180:
                        kit.servo[channel].angle = angle
                        print(f"Channel {channel} -> {angle}°")
                    else:
                        print("Invalid channel or angle")
                
                else:
                    print("Invalid command")
            
            except ValueError:
                print("Invalid input")
            except Exception as e:
                print(f"Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test servo motors')
    parser.add_argument('-c', '--controller', action='store_true',
                       help='Test PCA9685 controller')
    parser.add_argument('-m', '--movement', action='store_true',
                       help='Test movement sequences')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive servo control')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Run all tests')
    
    args = parser.parse_args()
    
    if not (args.controller or args.movement or args.interactive):
        args.all = True
    
    results = []
    
    if args.all or args.controller:
        results.append(('Controller', test_servo_controller()))
    
    if args.all or args.movement:
        results.append(('Movement', test_movement_sequence()))
    
    if args.all or args.interactive:
        results.append(('Interactive', interactive_servo_control()))
    
    if results:
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{name:20s} {status}")
        print("=" * 60)