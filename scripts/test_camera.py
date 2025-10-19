#!/usr/bin/env python3
"""
Test Camera - OV5647 Camera Module Testing
Tests camera initialization, capture, and performance
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("❌ OpenCV not available")
    OPENCV_AVAILABLE = False

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False

try:
    from picamera import PiCamera
    PICAMERA_LEGACY = True
except ImportError:
    PICAMERA_LEGACY = False

from config.hardware_config import CAMERA_CONFIG


def test_camera_detection():
    """Detect available cameras"""
    print("=" * 60)
    print("📹 Camera Detection")
    print("=" * 60)
    
    cameras_found = []
    
    # Test libcamera (Picamera2)
    if PICAMERA2_AVAILABLE:
        try:
            print("\n🔍 Testing Picamera2 (libcamera)...")
            cam = Picamera2()
            cameras_found.append("Picamera2 (libcamera)")
            print("   ✅ Picamera2 available")
            cam.close()
        except Exception as e:
            print(f"   ❌ Picamera2 failed: {e}")
    
    # Test legacy PiCamera
    if PICAMERA_LEGACY:
        try:
            print("\n🔍 Testing PiCamera (legacy)...")
            cam = PiCamera()
            cameras_found.append("PiCamera (legacy)")
            print("   ✅ PiCamera available")
            cam.close()
        except Exception as e:
            print(f"   ❌ PiCamera failed: {e}")
    
    # Test OpenCV cameras
    if OPENCV_AVAILABLE:
        print("\n🔍 Testing OpenCV cameras...")
        for idx in range(3):
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cameras_found.append(f"OpenCV Camera {idx}")
                        print(f"   ✅ Camera {idx} available ({frame.shape})")
                    cap.release()
            except:
                pass
    
    print("\n" + "=" * 60)
    print(f"📊 Found {len(cameras_found)} camera(s)")
    print("=" * 60)
    
    for cam in cameras_found:
        print(f"  • {cam}")
    
    return len(cameras_found) > 0


def test_camera_capture():
    """Test camera capture"""
    print("\n" + "=" * 60)
    print("📸 Camera Capture Test")
    print("=" * 60)
    
    try:
        from src.camera_ov5647 import OV5647Camera
        
        print("\n🎥 Initializing camera...")
        camera = OV5647Camera()
        
        if not camera.is_active():
            print("❌ Camera not active")
            return False
        
        print(f"✅ Camera active ({camera.get_camera_type()})")
        print(f"   Resolution: {camera.width}x{camera.height}")
        print(f"   FPS Target: {camera.fps_target}")
        
        # Start capture
        print("\n🎬 Starting capture...")
        camera.start_capture()
        time.sleep(2)  # Warmup
        
        # Test frame capture
        print("\n📷 Capturing frames...")
        for i in range(10):
            frame = camera.get_frame()
            if frame is not None:
                print(f"   Frame {i+1}: {frame.shape} - ✓")
            else:
                print(f"   Frame {i+1}: None - ✗")
            time.sleep(0.1)
        
        # Test FPS
        print(f"\n⚡ FPS: {camera.get_fps():.1f}")
        
        # Save test photo
        print("\n💾 Saving test photo...")
        filename = "images/test_camera_capture.jpg"
        if camera.save_frame(filename):
            print(f"   ✅ Saved: {filename}")
        else:
            print(f"   ❌ Save failed")
        
        # Cleanup
        camera.cleanup()
        print("\n✅ Camera test complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_camera_performance():
    """Test camera performance"""
    print("\n" + "=" * 60)
    print("⚡ Camera Performance Test")
    print("=" * 60)
    
    try:
        from src.camera_ov5647 import OV5647Camera
        
        camera = OV5647Camera()
        camera.start_capture()
        time.sleep(2)
        
        # FPS test
        print("\n🎯 FPS Test (10 seconds)...")
        frame_count = 0
        start_time = time.time()
        test_duration = 10
        
        while time.time() - start_time < test_duration:
            frame = camera.get_frame()
            if frame is not None:
                frame_count += 1
            time.sleep(0.001)
        
        actual_fps = frame_count / test_duration
        print(f"   Captured: {frame_count} frames")
        print(f"   Average FPS: {actual_fps:.2f}")
        print(f"   Target FPS: {camera.fps_target}")
        
        if actual_fps >= camera.fps_target * 0.8:
            print("   ✅ Performance acceptable")
        else:
            print("   ⚠️  Performance below target")
        
        # Latency test
        print("\n⏱️  Latency Test...")
        latencies = []
        for _ in range(10):
            start = time.time()
            frame = camera.get_frame()
            latency = (time.time() - start) * 1000  # ms
            if frame is not None:
                latencies.append(latency)
            time.sleep(0.1)
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            print(f"   Average: {avg_latency:.2f}ms")
            print(f"   Min: {min(latencies):.2f}ms")
            print(f"   Max: {max(latencies):.2f}ms")
        
        camera.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_camera_settings():
    """Test camera settings"""
    print("\n" + "=" * 60)
    print("⚙️  Camera Settings Test")
    print("=" * 60)
    
    print("\n📋 Current Configuration:")
    print(f"   Sensor: {CAMERA_CONFIG['sensor']}")
    print(f"   Resolution: {CAMERA_CONFIG['width']}x{CAMERA_CONFIG['height']}")
    print(f"   FPS: {CAMERA_CONFIG['fps']}")
    print(f"   Rotation: {CAMERA_CONFIG['rotation']}°")
    print(f"   Flip H: {CAMERA_CONFIG['flip_horizontal']}")
    print(f"   Flip V: {CAMERA_CONFIG['flip_vertical']}")
    print(f"   Brightness: {CAMERA_CONFIG['brightness']}")
    
    return True


def interactive_camera_view():
    """Interactive camera viewer"""
    print("\n" + "=" * 60)
    print("👁️  Interactive Camera View")
    print("=" * 60)
    
    if not OPENCV_AVAILABLE:
        print("❌ OpenCV required for interactive view")
        return False
    
    try:
        from src.camera_ov5647 import OV5647Camera
        
        print("\n🎥 Starting camera...")
        camera = OV5647Camera()
        camera.start_capture()
        time.sleep(1)
        
        print("\nControls:")
        print("  'q' - Quit")
        print("  's' - Save snapshot")
        print("  'f' - Toggle FPS display")
        
        show_fps = True
        snapshot_count = 0
        
        while True:
            frame = camera.get_frame()
            
            if frame is not None:
                display_frame = frame.copy()
                
                # Convert RGB to BGR for display
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)
                
                # Add FPS overlay
                if show_fps:
                    fps_text = f"FPS: {camera.get_fps():.1f}"
                    cv2.putText(display_frame, fps_text, (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow('Hey Spider Camera', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Exiting...")
                break
            elif key == ord('s'):
                snapshot_count += 1
                filename = f"images/snapshot_{snapshot_count:03d}.jpg"
                if camera.save_frame(filename):
                    print(f"📸 Saved: {filename}")
            elif key == ord('f'):
                show_fps = not show_fps
        
        cv2.destroyAllWindows()
        camera.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test OV5647 camera module',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 test_camera.py -d          # Detect cameras
  python3 test_camera.py -c          # Test capture
  python3 test_camera.py -p          # Test performance
  python3 test_camera.py -i          # Interactive view
  python3 test_camera.py -a          # Run all tests
        '''
    )
    
    parser.add_argument('-d', '--detect', action='store_true',
                       help='Detect available cameras')
    parser.add_argument('-c', '--capture', action='store_true',
                       help='Test camera capture')
    parser.add_argument('-p', '--performance', action='store_true',
                       help='Test camera performance')
    parser.add_argument('-s', '--settings', action='store_true',
                       help='Show camera settings')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive camera view')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Run all tests')
    
    args = parser.parse_args()
    
    # If no specific test selected, run all
    if not (args.detect or args.capture or args.performance or 
            args.settings or args.interactive):
        args.all = True
    
    results = []
    
    if args.all or args.detect:
        results.append(('Detection', test_camera_detection()))
        print()
    
    if args.all or args.settings:
        results.append(('Settings', test_camera_settings()))
        print()
    
    if args.all or args.capture:
        results.append(('Capture', test_camera_capture()))
        print()
    
    if args.all or args.performance:
        results.append(('Performance', test_camera_performance()))
        print()
    
    if args.interactive:
        results.append(('Interactive', interactive_camera_view()))
        print()
    
    # Summary
    if results:
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