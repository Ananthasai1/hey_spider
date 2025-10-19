"""
AI Thinking Engine - GPT Integration (Fixed for OpenAI v1.0+)
Processes robot state and makes decisions
"""

import threading
import time
import json
import re
from typing import Optional, Dict, List
from datetime import datetime

try:
    from openai import OpenAI
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
        
        # Performance tracking
        self.api_calls = 0
        self.api_errors = 0
        self.last_api_call = None
        
        # Initialize OpenAI
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client (v1.0+ compatible)"""
        if not OPENAI_AVAILABLE:
            print("⚠️  OpenAI library not available")
            print("   Install: pip install openai")
            return
        
        if not settings.OPENAI_API_KEY:
            print("⚠️  OpenAI API key not configured")
            print("   Set OPENAI_API_KEY in config/settings.py")
            return
        
        try:
            print("🧠 Initializing AI thinking engine...")
            
            # Create OpenAI client (v1.0+ style)
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=10.0,
                max_retries=2
            )
            
            # Test API connection with a minimal request
            print("   Testing API connection...")
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Reply with 'ok'"}
                ],
                max_tokens=5,
                timeout=5
            )
            
            test_content = test_response.choices[0].message.content
            
            print("✅ OpenAI client initialized successfully")
            print(f"   Model: {self.model}")
            print(f"   Test response: {test_content}")
            print(f"   API Version: v1.0+ compatible")
        
        except Exception as e:
            print(f"❌ OpenAI initialization error: {e}")
            print(f"   Error type: {type(e).__name__}")
            self.client = None
    
    def start_thinking(self):
        """Start AI thinking thread"""
        if self.running:
            print("⚠️  AI thinking already running")
            return
        
        if not self.client:
            print("⚠️  Cannot start thinking - OpenAI client not initialized")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._thinking_loop, daemon=True, name="AIThinking")
        self.thread.start()
        print("✅ AI thinking started")
        print(f"   Interval: {settings.AI_THINKING_INTERVAL}s")
    
    def stop_thinking(self):
        """Stop AI thinking thread"""
        if not self.running:
            return
        
        print("🛑 Stopping AI thinking...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
            if self.thread.is_alive():
                print("⚠️  AI thinking thread did not stop gracefully")
        
        print("✅ AI thinking stopped")
    
    def _thinking_loop(self):
        """Background thinking loop"""
        print("🧠 AI thinking loop started")
        
        while self.running:
            try:
                self._generate_thought()
                time.sleep(settings.AI_THINKING_INTERVAL)
            
            except Exception as e:
                print(f"❌ Thinking loop error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)  # Wait longer on error
        
        print("🧠 AI thinking loop ended")
    
    def _generate_thought(self):
        """Generate an AI thought based on current state"""
        try:
            # Gather context
            context = self._gather_context()
            
            if not self.client:
                # Mock thought when offline
                self._set_thought("Processing sensory input...", "neutral")
                return
            
            # Build prompt
            prompt = self._build_thought_prompt(context)
            
            # Call OpenAI API (v1.0+ style)
            self.api_calls += 1
            self.last_api_call = datetime.now()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Hey Spider Robot, a playful AI-powered quadruped robot. You are curious, friendly, and love exploring your environment. Always respond with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                timeout=5
            )
            
            # Extract content (v1.0+ style)
            content = response.choices[0].message.content
            
            # Parse JSON response
            self._parse_thought_response(content)
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            self.api_errors += 1
            self._set_thought("Thought formatting error", "puzzled")
        
        except Exception as e:
            print(f"❌ Thought generation error: {e}")
            self.api_errors += 1
            self._set_thought("Error in thought process", "puzzled")
    
    def _build_thought_prompt(self, context: Dict) -> str:
        """Build prompt for thought generation"""
        return f"""You are Hey Spider Robot, an AI-powered quadruped robot with vision and movement capabilities.

Current State:
- Mode: {context['mode']}
- Distance to objects: {context['distance']}cm
- Objects seen: {context['detections']}
- Movement status: {'Moving' if context['is_moving'] else 'Stationary'}
- Location: {context['location']}
- Time: {context['time']}

Generate a single short thought (max 30 words) about what the robot is currently thinking or observing. Be curious, playful, and personality-driven.

Then select one of these emotions: curious, alert, happy, focused, puzzled, tired, excited, calm

Respond ONLY with valid JSON in this exact format:
{{"thought": "your thought here", "emotion": "emotion"}}"""
    
    def _parse_thought_response(self, content: str):
        """Parse thought response from API"""
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                thought = data.get('thought', 'Thinking...')
                emotion = data.get('emotion', 'curious')
                
                # Validate emotion
                valid_emotions = ['curious', 'alert', 'happy', 'focused', 'puzzled', 'tired', 'excited', 'calm']
                if emotion not in valid_emotions:
                    emotion = 'curious'
                
                self._set_thought(thought, emotion)
            
            except json.JSONDecodeError:
                # Fallback if JSON is malformed
                self._set_thought(content[:50], 'neutral')
        else:
            # No JSON found, use raw content
            self._set_thought(content[:50], 'neutral')
    
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
        
        # Spider controller context
        if self.spider:
            try:
                context['mode'] = self.spider.current_mode
                context['is_moving'] = self.spider.is_moving
                context['distance'] = round(self.spider.get_distance(), 1)
            except Exception as e:
                print(f"⚠️  Error gathering spider context: {e}")
        
        # Vision context
        if self.vision:
            try:
                dets = self.vision.get_latest_detections()
                if dets:
                    classes = [d['class'] for d in dets[:3]]
                    context['detections'] = ', '.join(classes)
            except Exception as e:
                print(f"⚠️  Error gathering vision context: {e}")
        
        return context
    
    def _set_thought(self, thought: str, emotion: str):
        """Update current thought and emotion"""
        with self.thinking_lock:
            self.current_thought = thought[:100]  # Allow longer thoughts
            self.emotional_state = emotion
            
            # Add to history
            self.thoughts_history.append({
                'thought': thought,
                'emotion': emotion,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep last 100 thoughts
            if len(self.thoughts_history) > 100:
                self.thoughts_history.pop(0)
            
            # Update OLED display
            if self.oled:
                try:
                    self.oled.update_thought(thought[:50])  # OLED has less space
                except Exception as e:
                    print(f"⚠️  Error updating OLED: {e}")
            
            # Log thought
            print(f"💭 [{emotion.upper()}] {thought}")
    
    def process_command(self, command: str) -> str:
        """Process natural language command"""
        if not self.client:
            return json.dumps({
                'action': 'unknown',
                'response': 'AI system offline - no API key configured'
            })
        
        try:
            # Build prompt
            prompt = self._build_command_prompt(command)
            
            # Call OpenAI API
            self.api_calls += 1
            self.last_api_call = datetime.now()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Hey Spider Robot's command processor. Always respond with valid JSON containing an action and response."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=100,
                timeout=5
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json_match.group()
                # Validate JSON
                parsed = json.loads(result)
                
                # Ensure required fields
                if 'action' not in parsed or 'response' not in parsed:
                    return json.dumps({
                        'action': 'unknown',
                        'response': 'Invalid command format'
                    })
                
                return result
            else:
                return json.dumps({
                    'action': 'unknown',
                    'response': 'Could not parse command'
                })
        
        except json.JSONDecodeError as e:
            print(f"❌ Command processing JSON error: {e}")
            self.api_errors += 1
            return json.dumps({
                'action': 'unknown',
                'response': 'Error parsing AI response'
            })
        
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            self.api_errors += 1
            return json.dumps({
                'action': 'unknown',
                'response': f'Error: {str(e)}'
            })
    
    def _build_command_prompt(self, command: str) -> str:
        """Build prompt for command processing"""
        return f"""You are Hey Spider Robot. Process this command and decide what action to take.

Command: "{command}"

Available actions:
- walk_forward: Move forward
- walk_backward: Move backward  
- turn_left: Turn left
- turn_right: Turn right
- dance: Perform dance routine
- wave: Wave greeting
- take_photo: Capture photo
- stop: Stop all movement
- sit: Sit down
- stand: Stand up

Respond ONLY with valid JSON in this exact format:
{{"action": "action_name", "response": "short friendly response (max 20 words)"}}

Example responses:
{{"action": "walk_forward", "response": "Moving forward now!"}}
{{"action": "dance", "response": "Let me show you my moves!"}}
{{"action": "take_photo", "response": "Say cheese! Capturing photo now."}}

JSON response:"""
    
    def get_thought(self) -> Dict:
        """Get current thought"""
        with self.thinking_lock:
            return {
                'thought': self.current_thought,
                'emotion': self.emotional_state,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_thought_history(self, limit: int = 10) -> List[Dict]:
        """Get recent thoughts"""
        with self.thinking_lock:
            return self.thoughts_history[-limit:]
    
    def get_stats(self) -> Dict:
        """Get AI statistics"""
        success_rate = 0
        if self.api_calls > 0:
            success_rate = (self.api_calls - self.api_errors) / self.api_calls
        
        return {
            'api_calls': self.api_calls,
            'api_errors': self.api_errors,
            'success_rate': round(success_rate * 100, 1),
            'thoughts_stored': len(self.thoughts_history),
            'current_thought': self.current_thought,
            'current_emotion': self.emotional_state,
            'client_active': self.client is not None,
            'is_running': self.running,
            'last_api_call': self.last_api_call.isoformat() if self.last_api_call else None
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_thinking()
        
        # Log final stats
        if self.api_calls > 0:
            print(f"\n{'='*60}")
            print("📊 AI THINKING STATISTICS")
            print(f"{'='*60}")
            print(f"  Total API calls: {self.api_calls}")
            print(f"  Errors: {self.api_errors}")
            success_rate = (self.api_calls - self.api_errors) / self.api_calls * 100
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Thoughts generated: {len(self.thoughts_history)}")
            print(f"{'='*60}\n")
        
        print("✅ AI thinking cleanup complete")


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("🧪 TESTING AI THINKING ENGINE")
    print("="*60)
    
    # Mock components for testing
    class MockSpider:
        current_mode = "IDLE"
        is_moving = False
        
        def get_distance(self):
            return 42.5
    
    class MockVision:
        def get_latest_detections(self):
            return [
                {'class': 'person', 'confidence': 0.95},
                {'class': 'chair', 'confidence': 0.87},
                {'class': 'laptop', 'confidence': 0.78}
            ]
    
    class MockOLED:
        def update_thought(self, thought):
            pass
    
    # Create AI instance
    print("\n1️⃣  Initializing AI Thinking Engine...")
    ai = AIThinking(
        spider_controller=MockSpider(),
        vision_monitor=MockVision(),
        oled_display=MockOLED()
    )
    
    if not ai.client:
        print("\n❌ Cannot run tests - OpenAI client not initialized")
        print("   Make sure OPENAI_API_KEY is set in config/settings.py")
        exit(1)
    
    print("\n✅ OpenAI client initialized successfully")
    
    # Test command processing
    print("\n" + "="*60)
    print("2️⃣  TESTING COMMAND PROCESSING")
    print("="*60)
    
    test_commands = [
        "walk forward",
        "turn around and look behind you",
        "take a picture of what you see",
        "do a little dance for me",
        "stop what you're doing"
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n[Test {i}/5]")
        print(f"Command: '{cmd}'")
        result = ai.process_command(cmd)
        parsed = json.loads(result)
        print(f"Action: {parsed.get('action', 'N/A')}")
        print(f"Response: {parsed.get('response', 'N/A')}")
        time.sleep(1)
    
    # Test thought generation
    print("\n" + "="*60)
    print("3️⃣  TESTING AUTONOMOUS THOUGHT GENERATION")
    print("="*60)
    print("Starting AI thinking loop for 15 seconds...")
    
    ai.start_thinking()
    time.sleep(15)
    ai.stop_thinking()
    
    # Show thought history
    print("\n📜 Recent thoughts:")
    history = ai.get_thought_history(5)
    for i, thought in enumerate(history, 1):
        print(f"  {i}. [{thought['emotion'].upper()}] {thought['thought']}")
    
    # Show statistics
    print("\n" + "="*60)
    print("4️⃣  FINAL STATISTICS")
    print("="*60)
    
    stats = ai.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    print("\n" + "="*60)
    ai.cleanup()
    print("="*60)
    print("\n✅ Testing complete!")