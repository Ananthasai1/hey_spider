"""
AI Thinking Engine - GPT Integration
Processes robot state and makes decisions
"""

import threading
import time
import json
from typing import Optional, Dict, List
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI not available")
    OPENAI_AVAILABLE = False

from config.settings import settings
from src.oled_display import OLEDDisplay


class AIThinking:
    """AI engine for robot reasoning and decision making"""
    
    def __init__(self, spider_controller=None, vision_monitor=None, 
                 oled_display: Optional[OLEDDisplay] = None):
        self.spider = spider_controller
        self.vision = vision_monitor
        self.oled = oled_display
        
        # OpenAI client
        self.client = None
        self.model = settings.AI_MODEL
        
        # State
        self.running = False
        self.thread = None
        self.thinking_lock = threading.Lock()
        
        # Thoughts and mood
        self.current_thought = "Initializing..."
        self.emotional_state = "curious"
        self.thoughts_history = []
        
        # Initialize OpenAI
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            print("⚠️  OpenAI library not available")
            return
        
        if not settings.OPENAI_API_KEY:
            print("⚠️  OpenAI API key not configured")
            return
        
        try:
            print("🧠 Initializing AI thinking engine...")
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai
            print("✅ OpenAI client initialized")
        
        except Exception as e:
            print(f"❌ OpenAI initialization error: {e}")
            self.client = None
    
    def start_thinking(self):
        """Start AI thinking thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._thinking_loop, daemon=True)
        self.thread.start()
        print("✅ AI thinking started")
    
    def stop_thinking(self):
        """Stop AI thinking thread"""
        print("🛑 Stopping AI thinking...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        print("✅ AI thinking stopped")
    
    def _thinking_loop(self):
        """Background thinking loop"""
        while self.running:
            try:
                self._generate_thought()
                time.sleep(settings.AI_THINKING_INTERVAL)
            except Exception as e:
                print(f"❌ Thinking error: {e}")
                time.sleep(1)
    
    def _generate_thought(self):
        """Generate an AI thought based on current state"""
        try:
            # Gather context
            context = self._gather_context()
            
            if not self.client:
                # Mock thought
                self._set_thought("Processing sensory input...", "neutral")
                return
            
            # Call GPT
            prompt = f"""You are Hey Spider Robot, an AI-powered quadruped robot with vision and movement capabilities.

Current State:
- Mode: {context['mode']}
- Distance to objects: {context['distance']}cm
- Objects seen: {context['detections']}
- Movement status: {context['is_moving']}
- Location: {context['location']}

Respond with a single short thought (max 30 words) about what the robot is currently thinking or observing. Be curious, playful, and personality-driven. Then respond with one of these emotions: curious, alert, happy, focused, puzzled, or tired.

Format your response as JSON:
{{"thought": "your thought here", "emotion": "emotion"}}"""
            
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a playful AI robot named Hey Spider."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                timeout=5
            )
            
            # Parse response
            content = response.choices[0].message['content']
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                self._set_thought(data.get('thought', 'Thinking...'),
                                 data.get('emotion', 'curious'))
            else:
                self._set_thought(content[:50], 'neutral')
        
        except Exception as e:
            print(f"❌ Thought generation error: {e}")
            self._set_thought("Error in thought process", "puzzled")
    
    def _gather_context(self) -> Dict:
        """Gather robot state context"""
        context = {
            'mode': 'IDLE',
            'distance': 0.0,
            'detections': 'none',
            'is_moving': False,
            'location': 'unknown',
            'time': datetime.now().strftime("%H:%M:%S"),
        }
        
        if self.spider:
            context['mode'] = self.spider.current_mode
            context['is_moving'] = self.spider.is_moving
            context['distance'] = self.spider.get_distance()
        
        if self.vision:
            dets = self.vision.get_latest_detections()
            if dets:
                classes = [d['class'] for d in dets[:3]]
                context['detections'] = ', '.join(classes)
        
        return context
    
    def _set_thought(self, thought: str, emotion: str):
        """Update current thought and emotion"""
        with self.thinking_lock:
            self.current_thought = thought[:50]
            self.emotional_state = emotion
            self.thoughts_history.append({
                'thought': thought,
                'emotion': emotion,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep last 100 thoughts
            if len(self.thoughts_history) > 100:
                self.thoughts_history.pop(0)
            
            if self.oled:
                self.oled.update_thought(thought)
    
    def process_command(self, command: str) -> str:
        """Process natural language command"""
        if not self.client:
            return json.dumps({
                'action': 'unknown',
                'response': 'AI system offline'
            })
        
        try:
            prompt = f"""You are Hey Spider Robot. Process this command and decide what action to take.

Command: {command}

Available actions: walk_forward, turn_left, turn_right, dance, wave, take_photo, stop

Respond with JSON:
{{"action": "action_name", "response": "short response"}}"""
            
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI robot assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100,
                timeout=5
            )
            
            content = response.choices[0].message['content']
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json_match.group()
            else:
                return json.dumps({
                    'action': 'unknown',
                    'response': 'Could not parse command'
                })
        
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            return json.dumps({
                'action': 'unknown',
                'response': f'Error: {str(e)}'
            })
    
    def get_thought(self) -> Dict:
        """Get current thought"""
        with self.thinking_lock:
            return {
                'thought': self.current_thought,
                'emotion': self.emotional_state
            }
    
    def get_thought_history(self, limit: int = 10) -> List[Dict]:
        """Get recent thoughts"""
        with self.thinking_lock:
            return self.thoughts_history[-limit:]
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_thinking()
        print("✅ AI thinking cleanup complete")