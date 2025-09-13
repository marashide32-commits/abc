#!/usr/bin/env python3
"""
🤖 Humanoid Robot Brain - Main Entry Point
Raspberry Pi 5 Compatible AI System

This is the main orchestrator that starts all robot brain modules:
- Speech recognition (Bangla/English)
- Face recognition and memory
- AI conversation (Ollama + gemma:2b)
- Text-to-speech output
- Display management
- Internet search fallback

Author: AI Assistant
Compatible: Raspberry Pi 5 (8GB recommended)
"""

import sys
import os
import time
import threading
import signal
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import core modules
from core.intent import IntentRecognizer
from core.memory import MemoryManager
from core.task_manager import TaskManager
from core.config import Config

# Import system modules
from speech.stt import SpeechToText
from speech.tts_bangla import BanglaTTS
from speech.tts_english import EnglishTTS
from speech.audio_player import AudioPlayer

from vision.face_recognition import FaceRecognizer
from vision.camera_utils import CameraManager
from vision.vision_tasks import VisionTasks

from ai.ollama_client import OllamaClient
from ai.response_router import ResponseRouter

from ui.display_manager import DisplayManager
from ui.visualizer import SpectrumVisualizer
from ui.camera_view import CameraView

from actions.entertainment import EntertainmentModule
from actions.school_roles import SchoolRoleManager

class RobotBrain:
    """
    🧠 Main Robot Brain Class
    
    Orchestrates all subsystems and manages the robot's cognitive functions.
    Handles multimodal input (voice, vision, touch) and coordinates responses.
    """
    
    def __init__(self):
        """Initialize the robot brain with all subsystems."""
        print("🤖 Initializing Humanoid Robot Brain...")
        
        # Load configuration
        self.config = Config()
        
        # Initialize core brain components
        self.intent_recognizer = IntentRecognizer()
        self.memory_manager = MemoryManager()
        self.task_manager = TaskManager()
        
        # Initialize speech system
        self.stt = SpeechToText()
        self.bangla_tts = BanglaTTS()
        self.english_tts = EnglishTTS()
        self.audio_player = AudioPlayer()
        
        # Initialize vision system
        self.face_recognizer = FaceRecognizer()
        self.camera_manager = CameraManager()
        self.vision_tasks = VisionTasks(self.camera_manager, self.face_recognizer)
        
        # Initialize AI system
        self.ollama_client = OllamaClient()
        self.response_router = ResponseRouter(self.ollama_client)
        
        # Initialize UI system
        self.display_manager = DisplayManager()
        self.visualizer = SpectrumVisualizer()
        self.camera_view = CameraView()
        
        # Initialize action modules
        self.entertainment = EntertainmentModule()
        self.school_roles = SchoolRoleManager()
        
        # System state
        self.is_running = False
        self.current_user = None
        self.conversation_context = []
        
        print("✅ Robot Brain initialized successfully!")
    
    def start(self):
        """Start the robot brain and begin listening for interactions."""
        print("🚀 Starting Robot Brain...")
        self.is_running = True
        
        # Start background threads
        self.start_listening_thread()
        self.start_vision_thread()
        self.start_display_thread()
        
        # Welcome message
        self.speak_welcome()
        
        # Main interaction loop
        self.main_loop()
    
    def start_listening_thread(self):
        """Start continuous speech recognition in background thread."""
        def listen_continuously():
            while self.is_running:
                try:
                    # Listen for speech input
                    text, language = self.stt.listen()
                    if text:
                        print(f"👂 Heard ({language}): {text}")
                        self.process_speech_input(text, language)
                except Exception as e:
                    print(f"❌ STT Error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=listen_continuously, daemon=True)
        thread.start()
        print("🎤 Speech recognition started")
    
    def start_vision_thread(self):
        """Start continuous face recognition in background thread."""
        def recognize_faces():
            while self.is_running:
                try:
                    # Check for faces in camera feed
                    face_detected, person_info = self.face_recognizer.detect_and_identify()
                    if face_detected and person_info:
                        if person_info['name'] != self.current_user:
                            self.current_user = person_info['name']
                            self.greet_user(person_info)
                except Exception as e:
                    print(f"❌ Vision Error: {e}")
                    time.sleep(2)
        
        thread = threading.Thread(target=recognize_faces, daemon=True)
        thread.start()
        print("👁️ Face recognition started")
    
    def start_display_thread(self):
        """Start display management in background thread."""
        def manage_display():
            while self.is_running:
                try:
                    # Update display with current status
                    self.display_manager.update_status()
                    time.sleep(0.1)
                except Exception as e:
                    print(f"❌ Display Error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=manage_display, daemon=True)
        thread.start()
        print("🖥️ Display management started")
    
    def process_speech_input(self, text, language):
        """Process incoming speech and determine appropriate response."""
        try:
            # Recognize intent from speech
            intent = self.intent_recognizer.recognize(text, language)
            print(f"🎯 Intent: {intent}")
            
            # Add to conversation context
            self.conversation_context.append({
                'text': text,
                'language': language,
                'intent': intent,
                'timestamp': time.time()
            })
            
            # Route to task manager
            response = self.task_manager.handle_intent(intent, text, language, self.current_user)
            
            # Generate and deliver response
            self.deliver_response(response, language)
            
        except Exception as e:
            print(f"❌ Speech processing error: {e}")
            self.speak_error_response(language)
    
    def deliver_response(self, response, language):
        """Deliver the AI response through appropriate channels."""
        if not response:
            return
        
        # Display text response
        self.display_manager.show_text(response)
        
        # Convert to speech
        if language == 'bn':
            audio_file = self.bangla_tts.synthesize(response)
        else:
            audio_file = self.english_tts.synthesize(response)
        
        # Play audio with visualizer
        if audio_file:
            self.audio_player.play_with_visualizer(audio_file, self.visualizer)
    
    def greet_user(self, person_info):
        """Greet a recognized user with personalized message."""
        name = person_info['name']
        role = person_info.get('role', 'friend')
        
        if person_info.get('language_preference') == 'bn':
            greeting = f"আসসালামু আলাইকুম, {name}! আপনার সাথে দেখা করে ভালো লাগছে।"
        else:
            greeting = f"Hello {name}! Great to see you again."
        
        self.display_manager.show_text(greeting)
        self.deliver_response(greeting, person_info.get('language_preference', 'en'))
    
    def speak_welcome(self):
        """Speak initial welcome message."""
        welcome_bangla = "আসসালামু আলাইকুম! আমি আপনার রোবট সহকারী। আমি আপনার সাথে কথা বলতে এবং সাহায্য করতে প্রস্তুত।"
        welcome_english = "Hello! I'm your humanoid robot assistant. I'm ready to talk and help you."
        
        # Show both messages
        self.display_manager.show_text(f"{welcome_bangla}\n\n{welcome_english}")
        
        # Speak in Bangla first, then English
        self.deliver_response(welcome_bangla, 'bn')
        time.sleep(3)
        self.deliver_response(welcome_english, 'en')
    
    def speak_error_response(self, language):
        """Speak error message when something goes wrong."""
        if language == 'bn':
            error_msg = "দুঃখিত, আমি বুঝতে পারিনি। আবার বলুন দয়া করে।"
        else:
            error_msg = "Sorry, I didn't understand. Please try again."
        
        self.deliver_response(error_msg, language)
    
    def main_loop(self):
        """Main interaction loop - keeps robot running."""
        try:
            print("🤖 Robot Brain is now active and listening...")
            print("Press Ctrl+C to stop")
            
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Robot Brain...")
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all systems."""
        self.is_running = False
        
        # Cleanup resources
        self.camera_manager.cleanup()
        self.audio_player.cleanup()
        self.display_manager.cleanup()
        
        print("✅ Robot Brain shutdown complete")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Received shutdown signal...")
    sys.exit(0)

def main():
    """Main entry point for the robot brain."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start robot brain
        robot = RobotBrain()
        robot.start()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()