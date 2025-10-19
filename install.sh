#!/bin/bash

# Hey Spider Robot - Installation Script
# Run on Raspberry Pi with: bash install.sh

set -e  # Exit on error

echo "================================"
echo "🕷️  Hey Spider Robot Setup"
echo "================================"

# Check if running on Raspberry Pi
if ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is optimized for Raspberry Pi"
    echo "   But proceeding anyway..."
fi

# ============================================
# System Updates
# ============================================
echo ""
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# ============================================
# Python Setup
# ============================================
echo ""
echo "🐍 Setting up Python environment..."

# Install Python 3.9+
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo apt-get install -y python3-pip

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3.11 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip

# ============================================
# Hardware Dependencies
# ============================================
echo ""
echo "⚙️  Installing hardware dependencies..."

# I2C and GPIO
sudo apt-get install -y \
    i2c-tools \
    python3-smbus \
    python3-rpi.gpio

# Camera support (choose based on OS version)
echo "   Installing camera support..."
sudo apt-get install -y libatlas-base-dev libjasper-dev libtiff5 libjasper1 libharfbuzz0b libwebp6

# Audio support for voice recognition
sudo apt-get install -y portaudio19-dev

# ============================================
# Enable Interfaces
# ============================================
echo ""
echo "🔧 Enabling interfaces..."

# Enable I2C
if ! grep -q "i2c_arm=on" /boot/config.txt 2>/dev/null; then
    echo "   Enabling I2C..."
    echo "i2c_arm=on" | sudo tee -a /boot/config.txt > /dev/null
    echo "   ⚠️  I2C enabled - reboot required"
fi

# Enable Camera
if ! grep -q "start_x=1" /boot/config.txt 2>/dev/null; then
    echo "   Enabling Camera..."
    if grep -q "start_x=0" /boot/config.txt; then
        sudo sed -i 's/start_x=0/start_x=1/' /boot/config.txt
    else
        echo "start_x=1" | sudo tee -a /boot/config.txt > /dev/null
    fi
    echo "   ⚠️  Camera enabled - reboot required"
fi

# ============================================
# Python Dependencies
# ============================================
echo ""
echo "📚 Installing Python packages..."

pip install --upgrade setuptools wheel
pip install -r requirements.txt

# Install OpenCV (this takes a while)
echo "   Installing OpenCV (this may take 10+ minutes)..."
pip install opencv-python==4.8.1.78

# ============================================
# Project Structure
# ============================================
echo ""
echo "📁 Creating project directories..."

mkdir -p logs
mkdir -p images/{raw,detections}
mkdir -p data
mkdir -p models

# ============================================
# Configuration
# ============================================
echo ""
echo "⚙️  Setting up configuration..."

if [ ! -f ".env" ]; then
    echo "   Copying .env.example to .env..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your OpenAI API key"
else
    echo "   .env already exists"
fi

# ============================================
# Permissions
# ============================================
echo ""
echo "🔐 Setting up permissions..."

# Allow GPIO access without sudo
if ! getent group gpio > /dev/null; then
    sudo groupadd gpio
fi
sudo usermod -a -G gpio $(whoami)

echo "   ⚠️  GPIO permissions updated - reboot required"

# ============================================
# Test Calibration
# ============================================
echo ""
echo "🧪 Creating test scripts..."

cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""Quick setup test"""
import sys
sys.path.insert(0, '.')

print("Testing imports...")
try:
    import cv2
    print("✅ OpenCV")
except:
    print("❌ OpenCV")

try:
    import flask
    print("✅ Flask")
except:
    print("❌ Flask")

try:
    import RPi.GPIO
    print("✅ RPi.GPIO")
except:
    print("❌ RPi.GPIO (expected on non-Pi)")

try:
    from ultralytics import YOLO
    print("✅ YOLO")
except:
    print("❌ YOLO")

print("\nSetup appears ready!")
EOF

chmod +x test_setup.py

# ============================================
# Final Instructions
# ============================================
echo ""
echo "================================"
echo "✅ Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. REBOOT: sudo reboot"
echo "2. Edit .env: nano .env"
echo "3. Add your OpenAI API key"
echo "4. Run tests: python3 test_setup.py"
echo "5. Test hardware: python3 scripts/calibrate_sensors.py -a"
echo "6. Start robot: python3 main.py"
echo ""
echo "Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "For help:"
echo "   python3 main.py --help"
echo ""