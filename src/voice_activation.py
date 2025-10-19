"""
Voice Activation - Speech Recognition System
Wake word detection and command processing
"""

import threading
import time
from typing import Callable, Optional

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("⚠️  SpeechRecognition not available")
    SPEECH_RECOGNITION_AVAILABLE = False

from config.settings import settings
from src.oled_display import OLEDDisplay


class VoiceActivation:
    """Voice recognition and wake word detection"""
    
    def __init__(self, command_callback: Callable, 
                 oled_display: Optional[OLEDDisplay] = None):
        self.recognizer = None
        self.microphone = None
        self.running = False
        self.thread = None
        
        # Callback
        self.command_callback = command_callback
        self.oled = oled_display
        
        # Settings
        self.wake_phrase = settings.WAKE_PHRASE.lower()
        self.timeout = settings.VOICE_TIMEOUT
        self.language = settings.VOICE_LANGUAGE
        
        # Statistics
        self.commands_heard = 0
        self.false_positives = 0
        
        # Initialize
        self._initialize_recognition()
    
    def _initialize_recognition(self):
        """Initialize speech recognition"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("⚠️  SpeechRecognition not available - voice disabled")
            return
        
        try:
            print("🎙️  Initializing speech recognition...")
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            print("   Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("✅ Speech recognition initialized")
            print(f"   Wake phrase: '{self.wake_phrase}'")
            print(f"   Language: {self.language}")
        
        except Exception as e:
            print(f"❌ Speech recognition initialization failed: {e}")
            self.recognizer = None
            self.microphone = None
    
    def start_listening(self):
        """Start voice listening thread"""
        if self.running:
            return
        
        if not self.recognizer:
            print("⚠️  Voice system not available")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.thread.start()
        print("✅ Voice listening started")
    
    def stop_listening(self):
        """Stop voice listening"""
        print("🛑 Stopping voice listening...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        print("✅ Voice listening stopped")
    
    def _listening_loop(self):
        """Continuous listening loop"""
        while self.running:
            try:
                if self.microphone:
                    with self.microphone as source:
                        # Listen with timeout
                        audio = self.recognizer.listen(
                            source,
                            timeout=self.timeout,
                            phrase_time_limit=10
                        )
                    
                    # Process audio
                    self._process_audio(audio)
            
            except sr.UnknownValueError:
                # Audio not recognized - this is normal
                pass
            except sr.RequestError as e:
                print(f"❌ Recognition service error: {e}")
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Listening error: {e}")
                time.sleep(0.5)
    
    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            print("🔍 Processing audio...")
            
            # Try to recognize speech
            text = None
            
            # Try Google Speech Recognition first (free)
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.language
                )
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass
            
            if not text:
                return
            
            text_lower = text.lower()
            print(f"🎤 Heard: '{text}'")
            
            # Check for wake phrase
            if self.wake_phrase in text_lower:
                # Extract command
                command = text_lower.replace(self.wake_phrase, '').strip()
                
                if command:
                    print(f"✅ Wake word detected + command: '{command}'")
                    self.commands_heard += 1
                    
                    if self.oled:
                        self.oled.update_command(command[:15])
                    
                    # Execute callback
                    if self.command_callback:
                        self.command_callback(command)
                else:
                    print("⚠️  Wake word detected but no command")
                    self.false_positives += 1
        
        except Exception as e:
            print(f"❌ Audio processing error: {e}")
    
    def get_stats(self) -> dict:
        """Get voice recognition statistics"""
        return {
            'commands_heard': self.commands_heard,
            'false_positives': self.false_positives,
            'listening': self.running
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()
        print("✅ Voice activation cleanup complete")