#!/usr/bin/env python3
"""
Calibrate Sensors
Calibrates ultrasonic sensor and tests OLED display and I2C devices
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    print("⚠️  RPi.GPIO not available - using simulation")
    GPIO_AVAILABLE = False

from config.hardware_config import ULTRASONIC_PINS, I2C_CONFIG, SENSOR_CONFIG


def test_ultrasonic():
    """Test ultrasonic distance sensor"""
    print("=" * 60)
    print("📏 Ultrasonic Sensor Test")
    print("=" * 60)
    
    if not GPIO_AVAILABLE:
        print("❌ RPi.GPIO not available")
        return False
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ULTRASONIC_PINS['trigger'], GPIO.OUT)
        GPIO.setup(ULTRASONIC_PINS['echo'], GPIO.IN)
        
        print(f"✅ GPIO initialized")
        print(f"   Trigger: GPIO {ULTRASONIC_PINS['trigger']}")
        print(f"   Echo: GPIO {ULTRASONIC_PINS['echo']}")
        
        print("\n📊 Taking measurements...")
        print("   Press Ctrl+C to stop\n")
        
        measurements = []
        
        try:
            while True:
                # Trigger pulse
                GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.HIGH)
                time.sleep(0.00001)
                GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.LOW)
                
                # Wait for echo
                pulse_start = time.time()
                pulse_end = time.time()
                timeout = time.time() + 0.1
                
                while GPIO.input(ULTRASONIC_PINS['echo']) == GPIO.LOW:
                    pulse_start = time.time()
                    if pulse_start > timeout:
                        break
                
                while GPIO.input(ULTRASONIC_PINS['echo']) == GPIO.HIGH:
                    pulse_end = time.time()
                    if pulse_end > timeout:
                        break
                
                # Calculate distance
                pulse_duration = pulse_end - pulse_start
                distance = pulse_duration * 17150  # Speed of sound / 2
                distance = round(distance, 2)
                
                if distance < 400:  # Valid range
                    measurements.append(distance)
                    print(f"Distance: {distance:6.2f} cm", end='\r', flush=True)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
        
        # Statistics
        if measurements:
            print("\n" + "=" * 60)
            print("📊 Statistics")
            print("=" * 60)
            print(f"Measurements: {len(measurements)}")
            print(f"Min: {min(measurements):.2f} cm")
            print(f"Max: {max(measurements):.2f} cm")
            print(f"Average: {sum(measurements)/len(measurements):.2f} cm")
            print(f"Std Dev: {(sum((x - sum(measurements)/len(measurements))**2 for x in measurements)/len(measurements))**0.5:.2f}")
            print("=" * 60)
            return True
        else:
            print("❌ No valid measurements")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if GPIO_AVAILABLE:
            GPIO.cleanup()


def test_oled():
    """Test OLED display"""
    print("=" * 60)
    print("📺 OLED Display Test")
    print("=" * 60)
    
    try:
        import board
        import busio
        import adafruit_ssd1306
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ OLED libraries not installed")
        print("Install with: pip install adafruit-circuitpython-ssd1306 pillow")
        return False
    
    try:
        # Initialize I2C
        print(f"\n📡 Initializing I2C...")
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize display
        addr = SENSOR_CONFIG['oled']['address']
        print(f"   Connecting to OLED at 0x{addr:02X}...")
        display = adafruit_ssd1306.SSD1306_I2C(
            SENSOR_CONFIG['oled']['width'],
            SENSOR_CONFIG['oled']['height'],
            i2c,
            addr=addr
        )
        
        print("✅ OLED display initialized")
        
        # Clear display
        display.fill(0)
        display.show()
        
        # Load font
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
            )
        except:
            font = ImageFont.load_default()
        
        # Test patterns
        print("\n🎨 Testing patterns:")
        
        tests = [
            ("Fill White", lambda: draw.rectangle((0, 0, 127, 63), fill=255)),
            ("Fill Black", lambda: draw.rectangle((0, 0, 127, 63), fill=0)),
            ("Text", lambda: draw.text((10, 10), "Hey Spider", font=font, fill=255)),
            ("Border", lambda: draw.rectangle((0, 0, 127, 63), outline=255, fill=0)),
        ]
        
        for test_name, test_func in tests:
            print(f"   {test_name:15s}: ", end='', flush=True)
            
            image = Image.new('1', (128, 64))
            draw = ImageDraw.Draw(image)
            
            test_func()
            
            display.image(image)
            display.show()
            
            time.sleep(1)
            print("✓")
        
        # Animation test
        print(f"   Animation test : ", end='', flush=True)
        
        for frame in range(32):
            image = Image.new('1', (128, 64))
            draw = ImageDraw.Draw(image)
            
            draw.line((frame*4, 0, frame*4, 63), fill=255)
            draw.text((30, 25), f"Frame {frame}", font=font, fill=255)
            
            display.image(image)
            display.show()
            time.sleep(0.05)
        
        print("✓")
        
        # Final message
        image = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        draw.text((20, 20), "OLED Test OK!", font=font, fill=255)
        display.image(image)
        display.show()
        
        time.sleep(2)
        
        # Clear
        display.fill(0)
        display.show()
        
        print("\n✅ OLED test complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_i2c_devices():
    """Scan for I2C devices"""
    print("=" * 60)
    print("🔍 I2C Device Scanner")
    print("=" * 60)
    
    try:
        import smbus
    except ImportError:
        print("❌ smbus not available")
        print("Install with: sudo apt install python3-smbus")
        return False
    
    try:
        bus = smbus.SMBus(I2C_CONFIG['bus'])
        
        print(f"\n📡 Scanning I2C bus {I2C_CONFIG['bus']}...")
        print("   Address  Device")
        print("   " + "-" * 30)
        
        found_devices = []
        
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                device_name = "Unknown"
                
                if addr == 0x40:
                    device_name = "PCA9685 (Servo Controller)"
                elif addr == 0x3C:
                    device_name = "SSD1306 (OLED Display)"
                
                print(f"   0x{addr:02X}     {device_name}")
                found_devices.append((addr, device_name))
                
            except:
                pass
        
        if found_devices:
            print("\n✅ Found {} device(s)".format(len(found_devices)))
            return True
        else:
            print("\n⚠️  No I2C devices found")
            print("\nTroubleshooting:")
            print("  1. Enable I2C: sudo raspi-config")
            print("  2. Check connections")
            print("  3. Run: sudo i2cdetect -y 1")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_gpio_pins():
    """Test GPIO pin access"""
    print("=" * 60)
    print("🔌 GPIO Pin Test")
    print("=" * 60)
    
    if not GPIO_AVAILABLE:
        print("❌ RPi.GPIO not available")
        return False
    
    try:
        print("\n✅ GPIO module available")
        print(f"   GPIO version: {GPIO.VERSION}")
        print(f"   Board info: {GPIO.RPI_INFO}")
        
        # Test pin setup
        GPIO.setmode(GPIO.BCM)
        test_pin = 17
        
        GPIO.setup(test_pin, GPIO.OUT)
        print(f"\n   Test pin GPIO {test_pin}: OK")
        
        GPIO.output(test_pin, GPIO.HIGH)
        GPIO.output(test_pin, GPIO.LOW)
        print(f"   Test pin I/O: OK")
        
        GPIO.cleanup()
        
        print("\n✅ GPIO test complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main calibration tool"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Calibrate and test sensors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 calibrate_sensors.py -a          # Run all tests
  python3 calibrate_sensors.py -i          # I2C device scan
  python3 calibrate_sensors.py -u          # Ultrasonic sensor
  python3 calibrate_sensors.py -o          # OLED display
  python3 calibrate_sensors.py -g          # GPIO pins
        '''
    )
    
    parser.add_argument('-u', '--ultrasonic', action='store_true',
                       help='Test ultrasonic sensor')
    parser.add_argument('-o', '--oled', action='store_true',
                       help='Test OLED display')
    parser.add_argument('-i', '--i2c', action='store_true',
                       help='Scan I2C bus')
    parser.add_argument('-g', '--gpio', action='store_true',
                       help='Test GPIO pins')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Run all tests')
    
    args = parser.parse_args()
    
    # If no specific test selected, run all
    if not (args.ultrasonic or args.oled or args.i2c or args.gpio):
        args.all = True
    
    results = []
    
    if args.all or args.i2c:
        results.append(('I2C Scan', test_i2c_devices()))
        print()
    
    if args.all or args.gpio:
        results.append(('GPIO Pins', test_gpio_pins()))
        print()
    
    if args.all or args.ultrasonic:
        results.append(('Ultrasonic', test_ultrasonic()))
        print()
    
    if args.all or args.oled:
        results.append(('OLED', test_oled()))
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()