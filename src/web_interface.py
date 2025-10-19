"""
Web Interface - Flask + SocketIO Dashboard
Real-time web interface for robot control and monitoring
"""

import threading
import time
import base64
from datetime import datetime
from typing import Optional

try:
    from flask import Flask, render_template_string, jsonify
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    print("⚠️  Flask/SocketIO not available")
    FLASK_AVAILABLE = False

from config.settings import settings
from src.oled_display import OLEDDisplay


class WebInterface:
    """Flask web interface with SocketIO"""
    
    def __init__(self, spider_controller=None, vision_monitor=None,
                 ai_thinking=None, oled_display: Optional[OLEDDisplay] = None):
        self.spider = spider_controller
        self.vision = vision_monitor
        self.ai = ai_thinking
        self.oled = oled_display
        
        if not FLASK_AVAILABLE:
            print("⚠️  Flask not available - web interface disabled")
            self.app = None
            self.socketio = None
            return
        
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'hey-spider-robot-secret'
        
        # Initialize SocketIO
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            ping_timeout=settings.SOCKETIO_PING_TIMEOUT,
            ping_interval=settings.SOCKETIO_PING_INTERVAL
        )
        
        # Status
        self.running = False
        self.update_thread = None
        
        # Setup routes and events
        self._setup_routes()
        self._setup_socketio()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve dashboard HTML"""
            # Import from document 1
            html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕷️ Hey Spider Robot - Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #00d4ff;
            --bg-primary: #0a0e27;
            --text-primary: #ffffff;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
        }
        .container { max-width: 1800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.8em; background: linear-gradient(135deg, var(--primary), #ff00ff);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .panel { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
                 border-radius: 20px; padding: 25px; margin-bottom: 20px; }
        .btn { padding: 12px 24px; background: var(--primary); color: #000; border: none;
               border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn:hover { opacity: 0.8; }
        #videoFeed { width: 100%; border-radius: 15px; display: block; background: #000; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ HEY SPIDER ROBOT</h1>
            <p>Real-Time Control & Monitoring</p>
        </div>
        <div class="panel">
            <h2>Live Camera Feed</h2>
            <img id="videoFeed" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Crect fill='%23000'/%3E%3C/svg%3E">
        </div>
        <div class="panel">
            <h2>Controls</h2>
            <button class="btn" onclick="sendCommand('walk forward')">Forward</button>
            <button class="btn" onclick="sendCommand('turn left')">Left</button>
            <button class="btn" onclick="sendCommand('turn right')">Right</button>
            <button class="btn" onclick="sendCommand('dance')">Dance</button>
        </div>
    </div>
    <script>
        const socket = io();
        socket.on('status_update', (data) => {
            if (data.video_frame) {
                document.getElementById('videoFeed').src = 'data:image/jpeg;base64,' + data.video_frame;
            }
        });
        function sendCommand(cmd) {
            socket.emit('command', {command: cmd});
        }
    </script>
</body>
</html>"""
            return render_template_string(html_content)
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'spider': bool(self.spider),
                'vision': bool(self.vision),
                'ai': bool(self.ai)
            })
    
    def _setup_socketio(self):
        """Setup SocketIO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print("Client connected to web interface")
            emit('connection_response', {'data': 'Connected to Hey Spider Robot'})
        
        @self.socketio.on('command')
        def handle_command(data):
            """Handle robot command"""
            command = data.get('command', '')
            print(f"Web command received: {command}")
            
            if self.spider:
                try:
                    if 'forward' in command:
                        self.spider.walk_forward()
                    elif 'left' in command:
                        self.spider.turn_left()
                    elif 'right' in command:
                        self.spider.turn_right()
                    elif 'dance' in command:
                        self.spider.dance()
                    elif 'wave' in command:
                        self.spider.wave()
                    
                    emit('command_result', {'success': True, 'message': 'Command executed'})
                except Exception as e:
                    emit('command_result', {'success': False, 'message': str(e)})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected from web interface")
    
    def start(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Start web interface"""
        if not self.app:
            print("⚠️  Web interface not available")
            return
        
        print(f"🌐 Starting web interface on {host}:{port}")
        
        # Start status update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Start Flask app
        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    
    def _update_loop(self):
        """Broadcast status updates to clients"""
        while self.running:
            try:
                if self.vision:
                    frame = self.vision.get_annotated_frame()
                    if frame is not None:
                        from src.utils import frame_to_base64
                        frame_base64 = frame_to_base64(frame)
                        
                        status = {
                            'video_frame': frame_base64,
                            'distance': self.spider.get_distance() if self.spider else 0,
                            'is_moving': self.spider.is_moving if self.spider else False,
                            'detections': self.vision.get_latest_detections(),
                            'fps': self.vision.current_fps,
                        }
                        
                        if self.ai:
                            thought = self.ai.get_thought()
                            status['ai_thought'] = thought.get('thought')
                            status['emotional_state'] = thought.get('emotion')
                        
                        self.socketio.emit('status_update', status)
                
                time.sleep(0.1)  # Update every 100ms
            
            except Exception as e:
                print(f"Status update error: {e}")
                time.sleep(1)
    
    def stop(self):
        """Stop web interface"""
        print("Stopping web interface...")
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2)
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run web interface (alias for start)"""
        self.start(host, port, debug)