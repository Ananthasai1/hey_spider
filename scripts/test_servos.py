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
            # Center servos on interrupt
            for channel in servo_channels:
                try:
                    kit.servo[channel].angle = 90
                except:
                    pass
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_servo():
    """Test individual servo with detailed info"""
    if not SERVO_AVAILABLE:
        return False
    
    try:
        print("\n" + "=" * 60)
        print("🎯 Individual Servo Test")
        print("=" * 60)
        
        kit = ServoKit(channels=16)
        
        # Get channel from user
        print("\nAvailable servos:")
        for name, channel in sorted(SERVO_PINS.items()):
            print(f"  {channel:2d}: {name}")
        
        channel = int(input("\nEnter servo channel (0-15): "))
        
        if channel < 0 or channel > 15:
            print("❌ Invalid channel")
            return False
        
        print(f"\n🔧 Testing channel {channel}...")
        
        # Test sequence
        angles = [0, 45, 90, 135, 180, 90]
        
        for angle in angles:
            print(f"   Setting angle: {angle}°")
            kit.servo[channel].angle = angle
            time.sleep(1)
        
        print("✅ Test complete")
        return True
        
    except ValueError:
        print("❌ Invalid input")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
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
            ("Home Position", spider.go_home),
            ("Stand Up", spider.stand_up),
            ("Sit Down", spider.sit_down),
            ("Walk Forward (1 step)", lambda: spider.walk_forward(steps=1)),
            ("Turn Left (30°)", lambda: spider.turn_left(angle=30)),
            ("Turn Right (30°)", lambda: spider.turn_right(angle=30)),
            ("Dance", spider.dance),
            ("Wave", spider.wave),
        ]
        
        print("\n📋 Testing sequences:")
        print("   Press Enter to continue, 'q' to quit\n")
        
        for name, func in sequences:
            print(f"   {name:30s}: ", end='', flush=True)
            
            user_input = input()
            if user_input.lower() == 'q':
                print("\n🛑 Stopped by user")
                break
            
            try:
                func()
                print(f"   {'':30s}  ✓")
            except Exception as e:
                print(f"   {'':30s}  ✗ ({e})")
                continue
            
            time.sleep(0.5)
        
        # Return to home
        print("\n🏠 Returning to home position...")
        spider.go_home()
        
        print("\n✅ Movement test complete")
        spider.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_servo_calibration():
    """Calibrate servo ranges"""
    if not SERVO_AVAILABLE:
        return False
    
    try:
        print("\n" + "=" * 60)
        print("📐 Servo Calibration")
        print("=" * 60)
        
        kit = ServoKit(channels=16)
        
        print("\nThis will help you find the correct servo ranges.")
        print("For each servo, note the angles where:")
        print("  - The servo reaches minimum position")
        print("  - The servo reaches maximum position")
        print("  - The servo is in neutral/center position")
        
        calibration_data = {}
        
        for name, channel in sorted(SERVO_PINS.items())[:12]:  # First 12 servos
            print(f"\n📍 Calibrating: {name} (Channel {channel})")
            
            # Sweep to find range
            print("   Sweeping from 0° to 180°...")
            for angle in range(0, 181, 10):
                kit.servo[channel].angle = angle
                time.sleep(0.1)
            
            # Get user input
            try:
                min_angle = int(input("   Enter minimum safe angle: "))
                max_angle = int(input("   Enter maximum safe angle: "))
                center_angle = int(input("   Enter center/neutral angle: "))
                
                calibration_data[name] = {
                    'channel': channel,
                    'min': min_angle,
                    'max': max_angle,
                    'center': center_angle
                }
                
                # Set to center
                kit.servo[channel].angle = center_angle
                print(f"   ✅ Saved: min={min_angle}°, max={max_angle}°, center={center_angle}°")
                
            except ValueError:
                print("   ⚠️  Skipped due to invalid input")
                continue
            except KeyboardInterrupt:
                print("\n\n🛑 Calibration stopped")
                break
        
        # Save calibration data
        if calibration_data:
            import json
            filename = "data/servo_calibration.json"
            Path("data").mkdir(exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            print(f"\n💾 Calibration saved to: {filename}")
            print("\n📋 Calibration Summary:")
            for name, data in calibration_data.items():
                print(f"   {name:20s}: {data['min']}° - {data['center']}° - {data['max']}°")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
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
        print("  list               - List all servos")
        print("  quit               - Exit")
        
        while True:
            try:
                cmd = input("\n> ").strip().lower().split()
                
                if not cmd:
                    continue
                
                if cmd[0] == 'quit':
                    print("👋 Exiting...")
                    break
                
                elif cmd[0] == 'list':
                    print("\nConfigured Servos:")
                    for name, channel in sorted(SERVO_PINS.items()):
                        print(f"  {channel:2d}: {name}")
                
                elif cmd[0] == 'center':
                    print("Centering all servos...")
                    for i in range(16):
                        try:
                            kit.servo[i].angle = 90
                        except:
                            pass
                    print("✅ Done")
                
                elif cmd[0] == 'sweep' and len(cmd) > 1:
                    channel = int(cmd[1])
                    if 0 <= channel < 16:
                        print(f"Sweeping channel {channel}...")
                        for angle in range(0, 181, 10):
                            kit.servo[channel].angle = angle
                            print(f"  {angle}°", end='\r', flush=True)
                            time.sleep(0.1)
                        kit.servo[channel].angle = 90
                        print("\n✅ Done")
                    else:
                        print("❌ Invalid channel (0-15)")
                
                elif len(cmd) >= 2:
                    channel = int(cmd[0])
                    angle = int(cmd[1])
                    
                    if 0 <= channel < 16 and 0 <= angle <= 180:
                        kit.servo[channel].angle = angle
                        print(f"✅ Channel {channel} → {angle}°")
                    else:
                        print("❌ Invalid channel (0-15) or angle (0-180)")
                
                else:
                    print("❌ Invalid command. Type 'quit' to exit.")
            
            except ValueError:
                print("❌ Invalid input. Use: <channel> <angle>")
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Center all servos before exit
        print("\n🏠 Centering all servos...")
        for i in range(16):
            try:
                kit.servo[i].angle = 90
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_servo_speed():
    """Test servo movement speed"""
    if not SERVO_AVAILABLE:
        return False
    
    try:
        print("\n" + "=" * 60)
        print("⚡ Servo Speed Test")
        print("=" * 60)
        
        kit = ServoKit(channels=16)
        
        channel = int(input("\nEnter servo channel (0-15): "))
        
        if channel < 0 or channel > 15:
            print("❌ Invalid channel")
            return False
        
        print(f"\n🎯 Testing channel {channel}...")
        
        # Test different speeds
        speeds = [
            ("Slow", 0.05),
            ("Medium", 0.02),
            ("Fast", 0.01),
            ("Very Fast", 0.005)
        ]
        
        for speed_name, delay in speeds:
            print(f"\n   {speed_name} ({delay}s delay)...")
            
            start_time = time.time()
            for angle in range(0, 181, 5):
                kit.servo[channel].angle = angle
                time.sleep(delay)
            
            duration = time.time() - start_time
            print(f"   Time: {duration:.2f}s")
        
        # Return to center
        kit.servo[channel].angle = 90
        
        print("\n✅ Speed test complete")
        return True
        
    except ValueError:
        print("❌ Invalid input")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test servo motors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 test_servos.py -c          # Test controller
  python3 test_servos.py -m          # Test movements
  python3 test_servos.py -i          # Interactive control
  python3 test_servos.py -a          # Run all tests
        '''
    )
    
    parser.add_argument('-c', '--controller', action='store_true',
                       help='Test PCA9685 controller')
    parser.add_argument('-s', '--single', action='store_true',
                       help='Test individual servo')
    parser.add_argument('-m', '--movement', action='store_true',
                       help='Test movement sequences')
    parser.add_argument('-k', '--calibrate', action='store_true',
                       help='Calibrate servo ranges')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive servo control')
    parser.add_argument('-p', '--speed', action='store_true',
                       help='Test servo speed')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Run all tests')
    
    args = parser.parse_args()
    
    if not (args.controller or args.single or args.movement or 
            args.calibrate or args.interactive or args.speed):
        args.all = True
    
    results = []
    
    if args.all or args.controller:
        results.append(('Controller', test_servo_controller()))
    
    if args.single:
        results.append(('Individual', test_individual_servo()))
    
    if args.all or args.movement:
        results.append(('Movement', test_movement_sequence()))
    
    if args.calibrate:
        results.append(('Calibration', test_servo_calibration()))
    
    if args.speed:
        results.append(('Speed', test_servo_speed()))
    
    if args.interactive:
        results.append(('Interactive', interactive_servo_control()))
    
    if results:
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{name:20s} {status}")
        print("=" * 60)


if __name__ == "__main__":
    main()