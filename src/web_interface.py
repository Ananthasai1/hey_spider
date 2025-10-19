"""
Web Interface - Flask + SocketIO Dashboard
Real-time web interface for robot control and monitoring with advanced UI
"""

import threading
import time
import base64
import cv2
import numpy as np
from datetime import datetime
from typing import Optional

try:
    from flask import Flask, render_template, jsonify, send_from_directory
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    print("⚠️  Flask/SocketIO not available")
    FLASK_AVAILABLE = False

from config.settings import settings
from src.oled_display import OLEDDisplay


class WebInterface:
    """Flask web interface with SocketIO and advanced dashboard"""
    
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
        self.app.config['SECRET_KEY'] = 'hey-spider-robot-secret-key-2024'
        
        # Initialize SocketIO
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            ping_timeout=settings.SOCKETIO_PING_TIMEOUT,
            ping_interval=settings.SOCKETIO_PING_INTERVAL,
            async_mode='threading'
        )
        
        # Status
        self.running = False
        self.update_thread = None
        self.connected_clients = 0
        
        # Performance tracking
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        # Setup routes and events
        self._setup_routes()
        self._setup_socketio()
        
        print("✅ Web interface initialized")
    
    def _setup_routes(self):
        """Setup Flask HTTP routes"""
        
        @self.app.route('/')
        def index():
            """Serve main dashboard"""
            return self._get_dashboard_html()
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'spider': bool(self.spider),
                    'vision': bool(self.vision),
                    'ai': bool(self.ai),
                    'oled': bool(self.oled)
                },
                'clients': self.connected_clients
            })
        
        @self.app.route('/api/status')
        def api_status():
            """Get detailed robot status"""
            status = {
                'timestamp': datetime.now().isoformat(),
                'connected': True,
            }
            
            # Spider status
            if self.spider:
                status['spider'] = {
                    'mode': self.spider.current_mode,
                    'is_moving': self.spider.is_moving,
                    'distance': self.spider.get_distance()
                }
            
            # Vision status
            if self.vision:
                status['vision'] = {
                    'active': self.vision.is_camera_active(),
                    'fps': self.vision.current_fps,
                    'detections': len(self.vision.get_latest_detections())
                }
            
            # AI status
            if self.ai:
                thought = self.ai.get_thought()
                status['ai'] = {
                    'thought': thought.get('thought', ''),
                    'emotion': thought.get('emotion', 'neutral')
                }
            
            return jsonify(status)
        
        @self.app.route('/api/detections')
        def api_detections():
            """Get current object detections"""
            if self.vision:
                detections = self.vision.get_latest_detections()
                return jsonify({
                    'count': len(detections),
                    'detections': detections
                })
            return jsonify({'count': 0, 'detections': []})
    
    def _setup_socketio(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.connected_clients += 1
            print(f"✅ Client connected (total: {self.connected_clients})")
            
            emit('connection_response', {
                'status': 'connected',
                'message': 'Connected to Hey Spider Robot',
                'timestamp': datetime.now().isoformat()
            })
            
            # Send initial status
            self._send_initial_status()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.connected_clients = max(0, self.connected_clients - 1)
            print(f"❌ Client disconnected (remaining: {self.connected_clients})")
        
        @self.socketio.on('command')
        def handle_command(data):
            """Handle robot command from web interface"""
            command = data.get('command', '').lower().strip()
            print(f"🌐 Web command: '{command}'")
            
            if not command:
                emit('command_result', {
                    'success': False,
                    'message': 'Empty command'
                })
                return
            
            try:
                result = self._execute_command(command)
                emit('command_result', result)
                
                # Broadcast to all clients
                self.socketio.emit('command_executed', {
                    'command': command,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Command error: {e}")
                emit('command_result', {
                    'success': False,
                    'message': str(e)
                })
        
        @self.socketio.on('request_photo')
        def handle_photo_request():
            """Handle photo capture request"""
            print("📸 Photo requested via web")
            
            if self.vision:
                try:
                    filename = self.vision.capture_photo()
                    if filename:
                        emit('photo_captured', {
                            'success': True,
                            'filename': filename,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        emit('photo_captured', {
                            'success': False,
                            'message': 'Failed to capture photo'
                        })
                except Exception as e:
                    emit('photo_captured', {
                        'success': False,
                        'message': str(e)
                    })
        
        @self.socketio.on('voice_command')
        def handle_voice_command(data):
            """Handle voice command from web interface"""
            command = data.get('command', '')
            print(f"🎤 Voice command from web: '{command}'")
            
            # Process through AI if available
            if self.ai:
                try:
                    import json
                    response = self.ai.process_command(command)
                    parsed = json.loads(response)
                    
                    emit('voice_response', {
                        'success': True,
                        'response': parsed.get('response', 'Command processed')
                    })
                    
                except Exception as e:
                    emit('voice_response', {
                        'success': False,
                        'message': str(e)
                    })
    
    def _execute_command(self, command: str) -> dict:
        """Execute robot command and return result"""
        if not self.spider:
            return {
                'success': False,
                'message': 'Spider controller not available'
            }
        
        try:
            # Movement commands
            if any(word in command for word in ['forward', 'walk', 'ahead']):
                self.spider.walk_forward()
                return {'success': True, 'message': 'Moving forward'}
            
            elif 'back' in command or 'backward' in command:
                self.spider.walk_backward()
                return {'success': True, 'message': 'Moving backward'}
            
            elif 'left' in command:
                self.spider.turn_left()
                return {'success': True, 'message': 'Turning left'}
            
            elif 'right' in command:
                self.spider.turn_right()
                return {'success': True, 'message': 'Turning right'}
            
            # Action commands
            elif 'dance' in command:
                self.spider.dance()
                return {'success': True, 'message': 'Dancing!'}
            
            elif 'wave' in command or 'hello' in command:
                self.spider.wave()
                return {'success': True, 'message': 'Waving!'}
            
            elif 'sit' in command:
                self.spider.sit_down()
                return {'success': True, 'message': 'Sitting down'}
            
            elif 'stand' in command:
                self.spider.stand_up()
                return {'success': True, 'message': 'Standing up'}
            
            elif 'home' in command:
                self.spider.go_home()
                return {'success': True, 'message': 'Going to home position'}
            
            elif 'stop' in command:
                self.spider.stop()
                return {'success': True, 'message': 'Stopped'}
            
            # Photo command
            elif 'photo' in command or 'picture' in command:
                if self.vision:
                    filename = self.vision.capture_photo()
                    return {
                        'success': True,
                        'message': f'Photo captured: {filename}'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Camera not available'
                    }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown command: {command}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def _send_initial_status(self):
        """Send initial status to newly connected client"""
        status = {
            'timestamp': datetime.now().isoformat(),
        }
        
        if self.spider:
            status['spider'] = {
                'mode': self.spider.current_mode,
                'is_moving': self.spider.is_moving
            }
        
        if self.vision:
            status['vision'] = {
                'active': self.vision.is_camera_active(),
                'fps': self.vision.current_fps
            }
        
        emit('initial_status', status)
    
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
        
        # Start Flask app with SocketIO
        try:
            self.socketio.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                allow_unsafe_werkzeug=True
            )
        except Exception as e:
            print(f"❌ Web server error: {e}")
            self.stop()
    
    def _update_loop(self):
        """Broadcast real-time status updates to all connected clients"""
        print("✅ Status update thread started")
        
        while self.running:
            try:
                if self.connected_clients > 0:
                    # Prepare status update
                    status = {
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Video frame
                    if self.vision:
                        frame = self.vision.get_annotated_frame()
                        if frame is not None:
                            # Convert frame to JPEG
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            frame_base64 = base64.b64encode(buffer).decode('utf-8')
                            status['video_frame'] = frame_base64
                            
                            # Update FPS
                            self.frame_count += 1
                            current_time = time.time()
                            if current_time - self.last_frame_time >= 1.0:
                                status['stream_fps'] = self.frame_count
                                self.frame_count = 0
                                self.last_frame_time = current_time
                    
                    # Robot status
                    if self.spider:
                        status['distance'] = round(self.spider.get_distance(), 1)
                        status['is_moving'] = self.spider.is_moving
                        status['mode'] = self.spider.current_mode
                    
                    # Vision status
                    if self.vision:
                        detections = self.vision.get_latest_detections()
                        status['detections'] = detections
                        status['object_count'] = len(detections)
                        status['fps'] = self.vision.current_fps
                    
                    # AI thought
                    if self.ai:
                        thought = self.ai.get_thought()
                        status['ai_thought'] = thought.get('thought', '')
                        status['emotion'] = thought.get('emotion', 'neutral')
                    
                    # OLED status
                    if self.oled:
                        status['oled'] = {
                            'mode': self.oled.mode,
                            'distance': self.oled.distance,
                            'command': self.oled.command,
                            'fps': self.oled.fps
                        }
                    
                    # Broadcast to all clients
                    self.socketio.emit('status_update', status)
                
                # Update interval (10 FPS)
                time.sleep(0.1)
            
            except Exception as e:
                print(f"❌ Status update error: {e}")
                time.sleep(1)
        
        print("✅ Status update thread stopped")
    
    def stop(self):
        """Stop web interface"""
        print("🛑 Stopping web interface...")
        self.running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=2)
        
        print("✅ Web interface stopped")
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run web interface (alias for start)"""
        self.start(host, port, debug)
    
    def _get_dashboard_html(self) -> str:
        """Get complete dashboard HTML"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕷️ Hey Spider Robot - Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #00d4ff; --primary-dark: #0099cc; --secondary: #ff00ff;
            --secondary-dark: #cc00cc; --bg-primary: #0a0e27; --bg-secondary: #151932;
            --bg-tertiary: #1e2344; --text-primary: #ffffff; --text-secondary: #b8c5d6;
            --text-muted: #6b7a94; --success: #00ff88; --warning: #ffaa00;
            --error: #ff3366; --info: #00d4ff; --glass: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }
        body {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary); color: var(--text-primary);
            min-height: 100vh; overflow-x: hidden; position: relative;
        }
        body::before {
            content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 50%, rgba(255, 0, 255, 0.1) 0%, transparent 50%);
            animation: breathe 8s ease-in-out infinite; pointer-events: none; z-index: 0;
        }
        @keyframes breathe { 0%, 100% { opacity: 0.3; } 50% { opacity: 0.6; } }
        .container { position: relative; z-index: 1; max-width: 1800px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center; margin-bottom: 30px; padding: 30px;
            background: var(--glass); border: 1px solid var(--glass-border);
            border-radius: 20px; backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); position: relative; overflow: hidden;
        }
        .header::after {
            content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 212, 255, 0.1), transparent);
            animation: scan 3s linear infinite;
        }
        @keyframes scan {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        .header-content { position: relative; z-index: 1; }
        .logo {
            font-size: 4em; margin-bottom: 10px;
            filter: drop-shadow(0 0 20px var(--primary));
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
        h1 {
            font-size: 2.8em; margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; font-weight: 800; letter-spacing: -1px;
        }
        .subtitle { color: var(--text-secondary); font-size: 1.1em; margin-top: 10px; }
        .status-badge {
            display: inline-flex; align-items: center; gap: 10px;
            padding: 12px 24px; border-radius: 50px; font-weight: 600;
            margin-top: 20px; font-size: 0.95em; transition: all 0.3s ease; border: 2px solid;
        }
        .status-badge.connected {
            background: rgba(0, 255, 136, 0.1); border-color: var(--success);
            color: var(--success); box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        .status-badge.disconnected {
            background: rgba(255, 51, 102, 0.1); border-color: var(--error);
            color: var(--error); box-shadow: 0 0 20px rgba(255, 51, 102, 0.3);
        }
        .status-dot {
            width: 10px; height: 10px; border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        .connected .status-dot { background: var(--success); }
        .disconnected .status-dot { background: var(--error); }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        .dashboard {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px; margin-bottom: 20px;
        }
        .panel {
            background: var(--glass); border: 1px solid var(--glass-border);
            border-radius: 20px; padding: 25px; backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); transition: all 0.3s ease;
        }
        .panel:hover {
            border-color: rgba(0, 212, 255, 0.3);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4); transform: translateY(-5px);
        }
        .panel-header {
            display: flex; align-items: center; gap: 12px;
            margin-bottom: 20px; padding-bottom: 15px;
            border-bottom: 2px solid var(--glass-border);
        }
        .panel-icon { font-size: 1.8em; filter: drop-shadow(0 0 10px var(--primary)); }
        .panel h3 { font-size: 1.4em; font-weight: 700; color: var(--text-primary); }
        .video-panel { grid-column: span 2; }
        #videoFeed {
            width: 100%; border-radius: 15px; display: block; background: #000;
            min-height: 400px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            border: 2px solid var(--glass-border);
        }
        .controls {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 12px; margin-top: 20px;
        }
        .btn {
            padding: 16px; border: none; border-radius: 12px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white; font-size: 0.95em; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
            position: relative; overflow: hidden;
        }
        .btn::before {
            content: ''; position: absolute; top: 50%; left: 50%;
            width: 0; height: 0; border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%); transition: width 0.6s, height 0.6s;
        }
        .btn:hover::before { width: 300px; height: 300px; }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(0, 212, 255, 0.5);
        }
        .btn:active { transform: translateY(-1px); }
        .btn-secondary {
            background: linear-gradient(135deg, var(--secondary), var(--secondary-dark));
            box-shadow: 0 4px 15px rgba(255, 0, 255, 0.3);
        }
        .btn-secondary:hover { box-shadow: 0 6px 25px rgba(255, 0, 255, 0.5); }
        .stats-grid {
            display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;
        }
        .stat-item {
            background: var(--bg-tertiary); padding: 15px; border-radius: 12px;
            border-left: 4px solid var(--primary); transition: all 0.3s ease;
        }
        .stat-item:hover {
            border-left-color: var(--secondary); transform: translateX(5px);
        }
        .stat-label {
            color: var(--text-secondary); font-size: 0.85em;
            text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
        }
        .stat-value { font-size: 1.8em; font-weight: 700; color: var(--primary); }
        .detection-list { max-height: 300px; overflow-y: auto; }
        .detection-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: 12px; margin-bottom: 10px; background: var(--bg-tertiary);
            border-radius: 10px; border-left: 3px solid var(--primary);
            transition: all 0.3s ease;
        }
        .detection-item:hover {
            border-left-color: var(--secondary); transform: translateX(5px);
        }
        .detection-name { font-weight: 600; color: var(--text-primary); }
        .confidence { color: var(--success); font-weight: 700; font-size: 0.9em; }
        .ai-thought {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(255, 0, 255, 0.1));
            padding: 20px; border-radius: 15px; border: 1px solid var(--glass-border);
            font-style: italic; min-height: 80px; display: flex; align-items: center;
            font-size: 1.05em; color: var(--text-secondary);
        }
        @media (max-width: 900px) {
            .dashboard { grid-template-columns: 1fr; }
            .video-panel { grid-column: span 1; }
            .controls { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="logo">🕷️</div>
                <h1>HEY SPIDER ROBOT</h1>
                <p class="subtitle">AI-Powered Quadruped with Real-Time Vision & Control</p>
                <div id="connectionStatus" class="status-badge disconnected">
                    <div class="status-dot"></div>
                    <span>Connecting to robot...</span>
                </div>
            </div>
        </div>

        <div class="dashboard">
            <div class="panel video-panel">
                <div class="panel-header">
                    <span class="panel-icon">📹</span>
                    <h3>Live Camera Feed</h3>
                </div>
                <img id="videoFeed" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='400'%3E%3Crect width='100%25' height='100%25' fill='%23000'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='20' fill='%2300d4ff' text-anchor='middle' dy='.3em'%3EInitializing Camera...%3C/text%3E%3C/svg%3E" alt="Camera feed">
                
                <div class="controls">
                    <button class="btn" onclick="sendCommand('walk forward')">🚶 Forward</button>
                    <button class="btn" onclick="sendCommand('turn left')">↺ Left</button>
                    <button class="btn" onclick="sendCommand('turn right')">↻ Right</button>
                    <button class="btn btn-secondary" onclick="sendCommand('dance')">💃 Dance</button>
                    <button class="btn btn-secondary" onclick="sendCommand('wave')">👋 Wave</button>
                    <button class="btn" onclick="sendCommand('take photo')">📸 Photo</button>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span class="panel-icon">🤖</span>
                    <h3>Robot Status</h3>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Distance</div>
                        <div class="stat-value" id="distance">0 cm</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">FPS</div>
                        <div class="stat-value" id="fps">0</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Mode</div>
                        <div class="stat-value" id="mode">IDLE</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Objects</div>
                        <div class="stat-value" id="objectCount">0</div>
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span class="panel-icon">🧠</span>
                    <h3>AI Thoughts</h3>
                </div>
                <div class="ai-thought" id="aiThought">
                    Initializing AI thinking engine...
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span class="panel-icon">👁️</span>
                    <h3>Detected Objects</h3>
                </div>
                <div class="detection-list" id="detectionList">
                    <div style="text-align: center; color: var(--text-muted); padding: 20px;">
                        No objects detected yet...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', () => {
            console.log('Connected to robot');
            updateConnectionStatus(true);
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from robot');
            updateConnectionStatus(false);
        });

        socket.on('connection_response', (data) => {
            console.log('Connection response:', data);
        });

        socket.on('status_update', (data) => {
            if (data.video_frame) {
                document.getElementById('videoFeed').src = 'data:image/jpeg;base64,' + data.video_frame;
            }

            if (data.distance !== undefined) {
                document.getElementById('distance').textContent = data.distance + ' cm';
            }

            if (data.fps !== undefined) {
                document.getElementById('fps').textContent = data.fps;
            }

            if (data.mode !== undefined) {
                document.getElementById('mode').textContent = data.mode;
            }

            if (data.object_count !== undefined) {
                document.getElementById('objectCount').textContent = data.object_count;
            }

            if (data.ai_thought) {
                document.getElementById('aiThought').textContent = data.ai_thought;
            }

            if (data.detections) {
                updateDetections(data.detections);
            }
        });

        socket.on('command_result', (data) => {
            if (data.success) {
                console.log('✅', data.message);
            } else {
                console.log('❌', data.message);
            }
        });

        socket.on('photo_captured', (data) => {
            if (data.success) {
                console.log('📸 Photo captured:', data.filename);
            } else {
                console.log('❌ Photo failed:', data.message);
            }
        });

        function sendCommand(command) {
            console.log('Sending command:', command);
            socket.emit('command', { command: command });
        }

        function updateConnectionStatus(connected) {
            const statusBadge = document.getElementById('connectionStatus');
            if (connected) {
                statusBadge.className = 'status-badge connected';
                statusBadge.innerHTML = '<div class="status-dot"></div><span>Connected to Robot</span>';
            } else {
                statusBadge.className = 'status-badge disconnected';
                statusBadge.innerHTML = '<div class="status-dot"></div><span>Disconnected</span>';
            }
        }

        function updateDetections(detections) {
            const listElement = document.getElementById('detectionList');
            
            if (detections.length === 0) {
                listElement.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 20px;">No objects detected</div>';
                return;
            }

            let html = '';
            detections.forEach((det) => {
                const confidence = (det.confidence * 100).toFixed(0);
                html += `
                    <div class="detection-item">
                        <span class="detection-name">${det.class}</span>
                        <span class="confidence">${confidence}%</span>
                    </div>
                `;
            });
            
            listElement.innerHTML = html;
        }

        document.addEventListener('keydown', (e) => {
            switch(e.key.toLowerCase()) {
                case 'w':
                case 'arrowup':
                    sendCommand('walk forward');
                    e.preventDefault();
                    break;
                case 'a':
                case 'arrowleft':
                    sendCommand('turn left');
                    e.preventDefault();
                    break;
                case 'd':
                case 'arrowright':
                    sendCommand('turn right');
                    e.preventDefault();
                    break;
                case 's':
                case 'arrowdown':
                    sendCommand('walk backward');
                    e.preventDefault();
                    break;
                case ' ':
                    sendCommand('dance');
                    e.preventDefault();
                    break;
                case 'p':
                    sendCommand('take photo');
                    e.preventDefault();
                    break;
                case 'h':
                    sendCommand('wave');
                    e.preventDefault();
                    break;
            }
        });

        console.log('🕷️ Hey Spider Robot Dashboard initialized');
    </script>
</body>
</html>
        '''
        return html_content