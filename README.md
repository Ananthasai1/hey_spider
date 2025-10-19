# 🕷️ Hey Spider Robot v2.0

AI-Powered Quadruped Robot with Real-Time Vision and Voice Control

## Features

- **12-Servo Quadruped Movement** - Realistic spider-like locomotion with tripod gait
- **Real-Time Vision** - OV5647 camera with YOLO v8 object detection
- **AI Brain** - GPT-4 powered reasoning and decision making
- **Voice Control** - "Hey Spider" wake word + natural language commands
- **Web Dashboard** - Real-time monitoring and control interface
- **OLED Display** - On-robot status display
- **Ultrasonic Sensors** - Obstacle detection

## Hardware Requirements

- Raspberry Pi 4 (2GB+ RAM) or Pi 5
- OV5647 Camera Module
- PCA9685 Servo Controller (16-channel)
- 12x Servo Motors (9g or 15g)
- SSD1306 OLED Display (128x64)
- HC-SR04 Ultrasonic Sensor
- 5V Power Supply (10A+)
- Micro SD Card (64GB recommended)

## Quick Start

### 1. System Setup

```bash
cd hey_spider_robot
bash install.sh
sudo reboot
```

### 2. Configuration

```bash
nano .env
# Add your OpenAI API key
```

### 3. Test Hardware

```bash
source venv/bin/activate
python3 scripts/calibrate_sensors.py -a
python3 scripts/test_camera.py
```

### 4. Run Robot

```bash
python3 main.py
```

## Project Structure

```
hey_spider_robot/
├── main.py
├── requirements.txt
├── .env.example
├── install.sh
│
├── config/
│   ├── settings.py
│   ├── hardware_config.py
│   └── yolo_detection_config.py
│
├── src/
│   ├── spider_controller.py
│   ├── camera_ov5647.py
│   ├── visual_monitor.py
│   ├── ai_thinking.py
│   ├── voice_activation.py
│   ├── oled_display.py
│   ├── web_interface.py
│   └── utils.py
│
├── scripts/
│   ├── calibrate_sensors.py
│   ├── test_camera.py
│   └── test_servos.py
│
└── images/
    ├── raw/
    └── detections/
```

## Voice Commands

Say "Hey Spider" followed by:

- **Movement**: "walk forward", "turn left", "turn right", "stop"
- **Actions**: "dance", "wave", "sit down", "stand up"
- **Camera**: "take a photo", "what do you see"
- **Custom**: Natural language commands (AI processes them)

## Keyboard Controls (Web Dashboard)

- **W / ↑**: Walk forward
- **A / ←**: Turn left
- **D / →**: Turn right
- **Space**: Dance
- **P**: Take photo

## Web Dashboard

Access at: `http://raspberry-pi-ip:5000`

Features:
- Live camera feed with detections
- Real-time robot status
- Control buttons
- AI thoughts display
- Object detection list

## Troubleshooting

### Camera Not Working

```bash
# Check camera connection
vcgencmd get_camera

# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

### I2C Devices Not Detected

```bash
# Scan I2C bus
python3 scripts/calibrate_sensors.py -i

# Or use i2cdetect
i2cdetect -y 1
```

### Servo Not Moving

```bash
# Test PCA9685 connection
python3 scripts/calibrate_sensors.py -u

# Check servo power supply (5V)
# Verify servo connections
```

### Voice Recognition Issues

```bash
# Test microphone
arecord -D default -f cd -t wav /tmp/test_audio.wav
aplay /tmp/test_audio.wav

# Check audio levels
alsamixer
```

## Performance Optimization

### For Raspberry Pi 4

```bash
# Overclock CPU (optional, use with caution)
# Edit /boot/config.txt:
over_voltage=4
arm_freq=2000
```

### Reduce YOLO Model Size

```bash
# In .env, use smaller model:
YOLO_MODEL=yolov8n.pt  # Nano (fastest)
# Instead of yolov8m.pt (medium)
```

### Disable Logging (improves performance)

```bash
LOG_LEVEL=WARNING
```

## Development

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

### Run Tests

```bash
pytest tests/
```

## API Reference

### SpiderController

```python
from src.spider_controller import SpiderController

spider = SpiderController()
spider.walk_forward(steps=3)
spider.turn_left(angle=45)
spider.dance()
spider.get_distance()
```

### VisualMonitor

```python
from src.visual_monitor import VisualMonitor

vision = VisualMonitor()
vision.start_monitoring()
detections = vision.get_latest_detections()
frame = vision.get_latest_frame()
vision.capture_photo()
```

### AIThinking

```python
from src.ai_thinking import AIThinking

ai = AIThinking(spider, vision)
ai.start_thinking()
response = ai.process_command("walk forward")
```

## Debugging

### Enable Debug Mode

```bash
# In .env:
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Monitor System Resources

```bash
watch -n 1 'free -h; echo "---"; ps aux | grep python3'
```

### Check Logs

```bash
tail -f logs/spider.log
```

## Contributing

Contributions welcome! Please:

1. Follow PEP 8 style guide
2. Add docstrings to functions
3. Test on actual Raspberry Pi
4. Update README with changes

## License

MIT License - See LICENSE file

## Troubleshooting Checklist

- [ ] Raspberry Pi has internet connection
- [ ] All GPIO pins connected correctly
- [ ] I2C devices detected (i2cdetect -y 1)
- [ ] Camera enabled and tested
- [ ] OpenAI API key set in .env
- [ ] Virtual environment activated
- [ ] All dependencies installed (pip list)
- [ ] No other processes using GPIO/I2C

## Support

- Check logs: `tail -f logs/spider.log`
- Test hardware: `python3 scripts/calibrate_sensors.py -a`
- Common issues: See Troubleshooting section above

## Resources

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [YOLO Documentation](https://docs.ultralytics.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [PCA9685 Datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)