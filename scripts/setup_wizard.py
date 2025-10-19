# ============================================
# scripts/setup_wizard.py - CHANGE #9: Add Configuration Wizard
# Priority: 🟢 NICE-TO-HAVE
# NEW FILE - Create this file
# ============================================

#!/usr/bin/env python3
"""
Interactive Setup Wizard
Helps configure Hey Spider Robot with guided setup
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print("🕷️  HEY SPIDER ROBOT - INTERACTIVE SETUP WIZARD")
    print("="*60)
    print("\nThis wizard will help you configure your robot.")
    print("Press Ctrl+C at any time to cancel.\n")


def get_input(prompt: str, default: str = "", required: bool = False) -> str:
    """Get user input with default value"""
    if default:
        prompt = f"{prompt} [{default}]"
    prompt += ": "
    
    while True:
        value = input(prompt).strip()
        
        if not value and default:
            return default
        
        if not value and required:
            print("❌ This field is required. Please enter a value.")
            continue
        
        return value


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input"""
    default_str = "yes" if default else "no"
    response = get_input(f"{prompt} (yes/no)", default_str).lower()
    return response in ['yes', 'y', 'true', '1']


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format"""
    if not api_key:
        return True  # Allow empty
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
        return False
    
    if len(api_key) < 20:
        print("⚠️  Warning: API key seems too short")
        return False
    
    return True


def run_wizard():
    """Run the interactive setup wizard"""
    print_banner()
    
    env_vars = {}
    
    # ============================================
    # Section 1: OpenAI API Configuration
    # ============================================
    print("┌────────────────────────────────────────────────────────┐")
    print("│ 1️⃣  OPENAI API CONFIGURATION                           │")
    print("└────────────────────────────────────────────────────────┘")
    print("\nThe robot uses OpenAI GPT for AI thinking and commands.")
    print("Get your API key from: https://platform.openai.com/api-keys")
    print("(You can skip this and add it later in .env file)\n")
    
    while True:
        api_key = get_input("Enter your OpenAI API key (or press Enter to skip)", "")
        if not api_key or validate_api_key(api_key):
            break
    
    if api_key:
        env_vars['OPENAI_API_KEY'] = api_key
        
        # AI Model selection
        print("\nAvailable AI models:")
        print("  1. gpt-4 (recommended, more capable)")
        print("  2. gpt-3.5-turbo (faster, cheaper)")
        
        model_choice = get_input("Choose model (1/2)", "1")
        env_vars['AI_MODEL'] = 'gpt-4' if model_choice == '1' else 'gpt-3.5-turbo'
        
        print(f"✅ AI configured with {env_vars['AI_MODEL']}")
    else:
        print("⚠️  Skipped - AI features will be limited")
    
    # ============================================
    # Section 2: Camera Configuration
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 2️⃣  CAMERA CONFIGURATION                               │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    camera_enabled = get_yes_no("Enable camera", True)
    env_vars['CAMERA_ENABLED'] = 'true' if camera_enabled else 'false'
    
    if camera_enabled:
        print("\nCamera resolution presets:")
        print("  1. 640x480 (VGA, recommended)")
        print("  2. 1280x720 (HD, slower)")
        print("  3. Custom")
        
        res_choice = get_input("Choose resolution (1/2/3)", "1")
        
        if res_choice == '2':
            env_vars['CAMERA_WIDTH'] = '1280'
            env_vars['CAMERA_HEIGHT'] = '720'
        elif res_choice == '3':
            env_vars['CAMERA_WIDTH'] = get_input("Width", "640")
            env_vars['CAMERA_HEIGHT'] = get_input("Height", "480")
        else:
            env_vars['CAMERA_WIDTH'] = '640'
            env_vars['CAMERA_HEIGHT'] = '480'
        
        # FPS
        fps = get_input("Camera FPS (frames per second)", "30")
        env_vars['CAMERA_FPS'] = fps
        
        print(f"✅ Camera configured: {env_vars['CAMERA_WIDTH']}x{env_vars['CAMERA_HEIGHT']} @ {fps}fps")
    
    # ============================================
    # Section 3: Object Detection
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 3️⃣  OBJECT DETECTION CONFIGURATION                     │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    print("YOLO model selection:")
    print("  1. yolov8n.pt (nano, fastest, recommended)")
    print("  2. yolov8s.pt (small, balanced)")
    print("  3. yolov8m.pt (medium, slower but more accurate)")
    
    yolo_choice = get_input("Choose YOLO model (1/2/3)", "1")
    models = {'1': 'yolov8n.pt', '2': 'yolov8s.pt', '3': 'yolov8m.pt'}
    env_vars['YOLO_MODEL'] = models.get(yolo_choice, 'yolov8n.pt')
    
    # Confidence threshold
    confidence = get_input("Detection confidence threshold (0.0-1.0)", "0.5")
    env_vars['CONFIDENCE_THRESHOLD'] = confidence
    
    print(f"✅ Detection configured with {env_vars['YOLO_MODEL']}")
    
    # ============================================
    # Section 4: Web Interface
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 4️⃣  WEB INTERFACE CONFIGURATION                        │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    port = get_input("Web interface port", "5000")
    env_vars['WEB_PORT'] = port
    
    host = get_input("Web interface host (0.0.0.0 for all interfaces)", "0.0.0.0")
    env_vars['WEB_HOST'] = host
    
    print(f"✅ Web interface will be available at http://{host}:{port}")
    
    # ============================================
    # Section 5: Hardware Configuration
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 5️⃣  HARDWARE CONFIGURATION                             │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    print("Are you running on:")
    print("  1. Raspberry Pi with real hardware (servos, sensors)")
    print("  2. Development machine (mock hardware for testing)")
    
    hw_choice = get_input("Choose (1/2)", "1")
    env_vars['MOCK_HARDWARE'] = 'false' if hw_choice == '1' else 'true'
    
    if hw_choice == '1':
        print("\n⚙️  Real hardware mode")
        print("   Make sure all hardware is connected:")
        print("   - PCA9685 servo controller")
        print("   - OV5647 camera module")
        print("   - SSD1306 OLED display")
        print("   - HC-SR04 ultrasonic sensor")
    else:
        print("\n💻 Development mode - hardware will be simulated")
    
    # ============================================
    # Section 6: Voice Control (Optional)
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 6️⃣  VOICE CONTROL (OPTIONAL)                           │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    voice_enabled = get_yes_no("Configure voice control", False)
    
    if voice_enabled:
        wake_phrase = get_input("Wake phrase", "hey spider")
        env_vars['WAKE_PHRASE'] = wake_phrase
        
        timeout = get_input("Voice timeout (seconds)", "5")
        env_vars['VOICE_TIMEOUT'] = timeout
        
        print(f"✅ Voice control configured with wake phrase: '{wake_phrase}'")
    
    # ============================================
    # Section 7: Logging
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 7️⃣  LOGGING CONFIGURATION                              │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    print("Log level:")
    print("  1. INFO (recommended, balanced logging)")
    print("  2. DEBUG (verbose, for troubleshooting)")
    print("  3. WARNING (minimal logging)")
    
    log_choice = get_input("Choose log level (1/2/3)", "1")
    log_levels = {'1': 'INFO', '2': 'DEBUG', '3': 'WARNING'}
    env_vars['LOG_LEVEL'] = log_levels.get(log_choice, 'INFO')
    
    # ============================================
    # Save Configuration
    # ============================================
    print("\n┌────────────────────────────────────────────────────────┐")
    print("│ 💾 SAVING CONFIGURATION                                │")
    print("└────────────────────────────────────────────────────────┘\n")
    
    env_path = Path('.env')
    
    # Backup existing .env
    if env_path.exists():
        backup_path = Path('.env.backup')
        print(f"⚠️  Existing .env found - backing up to {backup_path}")
        import shutil
        shutil.copy(env_path, backup_path)
    
    # Write new .env
    try:
        with open(env_path, 'w') as f:
            f.write("# Hey Spider Robot Configuration\n")
            f.write("# Generated by setup wizard\n")
            f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write variables by section
            f.write("# ============================================\n")
            f.write("# OpenAI API Configuration\n")
            f.write("# ============================================\n")
            if 'OPENAI_API_KEY' in env_vars:
                f.write(f"OPENAI_API_KEY={env_vars['OPENAI_API_KEY']}\n")
                f.write(f"AI_MODEL={env_vars.get('AI_MODEL', 'gpt-4')}\n")
            f.write("\n")
            
            f.write("# ============================================\n")
            f.write("# Camera Settings\n")
            f.write("# ============================================\n")
            f.write(f"CAMERA_ENABLED={env_vars.get('CAMERA_ENABLED', 'true')}\n")
            if 'CAMERA_WIDTH' in env_vars:
                f.write(f"CAMERA_WIDTH={env_vars['CAMERA_WIDTH']}\n")
                f.write(f"CAMERA_HEIGHT={env_vars['CAMERA_HEIGHT']}\n")
                f.write(f"CAMERA_FPS={env_vars.get('CAMERA_FPS', '30')}\n")
            f.write("\n")
            
            f.write("# ============================================\n")
            f.write("# Vision Detection\n")
            f.write("# ============================================\n")
            f.write(f"YOLO_MODEL={env_vars.get('YOLO_MODEL', 'yolov8n.pt')}\n")
            f.write(f"CONFIDENCE_THRESHOLD={env_vars.get('CONFIDENCE_THRESHOLD', '0.5')}\n")
            f.write("\n")
            
            f.write("# ============================================\n")
            f.write("# Web Interface\n")
            f.write("# ============================================\n")
            f.write(f"WEB_PORT={env_vars.get('WEB_PORT', '5000')}\n")
            f.write(f"WEB_HOST={env_vars.get('WEB_HOST', '0.0.0.0')}\n")
            f.write("\n")
            
            f.write("# ============================================\n")
            f.write("# Hardware Settings\n")
            f.write("# ============================================\n")
            f.write(f"MOCK_HARDWARE={env_vars.get('MOCK_HARDWARE', 'false')}\n")
            f.write("\n")
            
            if 'WAKE_PHRASE' in env_vars:
                f.write("# ============================================\n")
                f.write("# Voice Settings\n")
                f.write("# ============================================\n")
                f.write(f"WAKE_PHRASE={env_vars['WAKE_PHRASE']}\n")
                f.write(f"VOICE_TIMEOUT={env_vars.get('VOICE_TIMEOUT', '5')}\n")
                f.write("\n")
            
            f.write("# ============================================\n")
            f.write("# Logging\n")
            f.write("# ============================================\n")
            f.write(f"LOG_LEVEL={env_vars.get('LOG_LEVEL', 'INFO')}\n")
        
        print(f"✅ Configuration saved to {env_path}")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False
    
    # ============================================
    # Next Steps
    # ============================================
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next steps:")
    print("   1. Check system requirements: make check")
    print("   2. Calibrate sensors: make calibrate")
    print("   3. Test camera: python3 scripts/test_camera.py")
    print("   4. Run the robot: make run")
    print("\n🌐 Web interface will be available at:")
    print(f"   http://localhost:{env_vars.get('WEB_PORT', '5000')}")
    print("\n" + "="*60 + "\n")
    
    return True


if __name__ == "__main__":
    from datetime import datetime
    
    try:
        success = run_wizard()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)