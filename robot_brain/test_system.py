#!/usr/bin/env python3
"""
🧪 Robot Brain System Test Suite

Comprehensive testing script for all robot brain components.
Run this to verify that all systems are working correctly.
"""

import sys
import time
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from core.config import Config
        from core.intent import IntentRecognizer
        from core.memory import MemoryManager
        from core.task_manager import TaskManager
        
        from speech.stt import SpeechToText
        from speech.tts_bangla import BanglaTTS
        from speech.tts_english import EnglishTTS
        from speech.audio_player import AudioPlayer
        
        from vision.face_recognition import FaceRecognizer
        from vision.camera_utils import CameraManager
        from vision.vision_tasks import VisionTasks
        
        from ai.ollama_client import OllamaClient
        from ai.response_router import ResponseRouter
        from ai.web_search import WebSearcher
        
        from ui.display_manager import DisplayManager
        from ui.visualizer import SpectrumVisualizer
        from ui.camera_view import CameraView
        
        from actions.entertainment import EntertainmentModule
        from actions.school_roles import SchoolRoleManager
        from actions.motion import MotionController
        
        print("✅ All modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_core_modules():
    """Test core brain modules."""
    print("\n🧪 Testing core modules...")
    
    try:
        # Test configuration
        from core.config import Config
        config = Config()
        print("✅ Configuration loaded")
        
        # Test intent recognition
        from core.intent import IntentRecognizer
        intent_recognizer = IntentRecognizer()
        
        # Test Bangla intent
        intent = intent_recognizer.recognize("আসসালামু আলাইকুম", "bn")
        print(f"✅ Bangla intent recognition: {intent.type.value}")
        
        # Test English intent
        intent = intent_recognizer.recognize("Hello, how are you?", "en")
        print(f"✅ English intent recognition: {intent.type.value}")
        
        # Test memory manager
        from core.memory import MemoryManager
        memory = MemoryManager()
        print("✅ Memory manager initialized")
        
        # Test task manager
        from core.task_manager import TaskManager
        task_manager = TaskManager()
        print("✅ Task manager initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Core modules error: {e}")
        traceback.print_exc()
        return False

def test_speech_system():
    """Test speech processing system."""
    print("\n🧪 Testing speech system...")
    
    try:
        # Test STT
        from speech.stt import SpeechToText
        stt = SpeechToText()
        print("✅ Speech-to-text initialized")
        
        # Test microphone
        if stt.test_microphone():
            print("✅ Microphone test passed")
        else:
            print("⚠️ Microphone test failed (may not be available)")
        
        # Test Bangla TTS
        from speech.tts_bangla import BanglaTTS
        bangla_tts = BanglaTTS()
        if bangla_tts.is_initialized:
            print("✅ Bangla TTS initialized")
        else:
            print("⚠️ Bangla TTS not available (Coqui TTS not installed)")
        
        # Test English TTS
        from speech.tts_english import EnglishTTS
        english_tts = EnglishTTS()
        if english_tts.is_initialized:
            print("✅ English TTS initialized")
        else:
            print("⚠️ English TTS not available (Piper TTS not installed)")
        
        # Test audio player
        from speech.audio_player import AudioPlayer
        audio_player = AudioPlayer()
        print("✅ Audio player initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Speech system error: {e}")
        traceback.print_exc()
        return False

def test_vision_system():
    """Test computer vision system."""
    print("\n🧪 Testing vision system...")
    
    try:
        # Test camera manager
        from vision.camera_utils import CameraManager
        camera_manager = CameraManager()
        
        if camera_manager.is_initialized:
            print("✅ Camera manager initialized")
            
            # Test camera
            if camera_manager.test_camera():
                print("✅ Camera test passed")
            else:
                print("⚠️ Camera test failed")
        else:
            print("⚠️ Camera not available")
        
        # Test face recognition
        from vision.face_recognition import FaceRecognizer
        face_recognizer = FaceRecognizer()
        print("✅ Face recognition initialized")
        
        # Test vision tasks
        from vision.vision_tasks import VisionTasks
        vision_tasks = VisionTasks(camera_manager, face_recognizer)
        print("✅ Vision tasks initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Vision system error: {e}")
        traceback.print_exc()
        return False

def test_ai_system():
    """Test AI integration system."""
    print("\n🧪 Testing AI system...")
    
    try:
        # Test Ollama client
        from ai.ollama_client import OllamaClient
        ollama_client = OllamaClient()
        
        if ollama_client.is_available:
            print("✅ Ollama client connected")
            
            # Test model
            if ollama_client.test_model():
                print("✅ AI model test passed")
            else:
                print("⚠️ AI model test failed")
        else:
            print("⚠️ Ollama not available")
        
        # Test response router
        from ai.response_router import ResponseRouter
        response_router = ResponseRouter(ollama_client)
        print("✅ Response router initialized")
        
        # Test web search
        from ai.web_search import WebSearcher
        web_searcher = WebSearcher()
        if web_searcher.is_available:
            print("✅ Web search available")
        else:
            print("⚠️ Web search not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ AI system error: {e}")
        traceback.print_exc()
        return False

def test_ui_system():
    """Test user interface system."""
    print("\n🧪 Testing UI system...")
    
    try:
        # Test display manager
        from ui.display_manager import DisplayManager
        display_manager = DisplayManager()
        print("✅ Display manager initialized")
        
        # Test visualizer
        from ui.visualizer import SpectrumVisualizer
        visualizer = SpectrumVisualizer()
        print("✅ Spectrum visualizer initialized")
        
        # Test camera view
        from ui.camera_view import CameraView
        camera_view = CameraView()
        print("✅ Camera view initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ UI system error: {e}")
        traceback.print_exc()
        return False

def test_action_modules():
    """Test action modules."""
    print("\n🧪 Testing action modules...")
    
    try:
        # Test entertainment module
        from actions.entertainment import EntertainmentModule
        entertainment = EntertainmentModule()
        
        # Test Bangla content
        bangla_content = entertainment.get_general_content('bn')
        print(f"✅ Bangla entertainment: {bangla_content[:50]}...")
        
        # Test English content
        english_content = entertainment.get_general_content('en')
        print(f"✅ English entertainment: {english_content[:50]}...")
        
        # Test school roles
        from actions.school_roles import SchoolRoleManager
        school_roles = SchoolRoleManager()
        print("✅ School role manager initialized")
        
        # Test motion controller
        from actions.motion import MotionController
        motion_controller = MotionController()
        print("✅ Motion controller initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Action modules error: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test system integration."""
    print("\n🧪 Testing system integration...")
    
    try:
        # Test main system components working together
        from core.intent import IntentRecognizer
        from core.task_manager import TaskManager
        
        intent_recognizer = IntentRecognizer()
        task_manager = TaskManager()
        
        # Test Bangla question
        intent = intent_recognizer.recognize("কৃত্রিম বুদ্ধিমত্তা কি?", "bn")
        print(f"✅ Bangla question intent: {intent.type.value}")
        
        # Test English question
        intent = intent_recognizer.recognize("What is artificial intelligence?", "en")
        print(f"✅ English question intent: {intent.type.value}")
        
        # Test camera capture intent
        intent = intent_recognizer.recognize("ছবি তুলো", "bn")
        print(f"✅ Camera capture intent: {intent.type.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        traceback.print_exc()
        return False

def run_performance_test():
    """Run basic performance tests."""
    print("\n🧪 Running performance tests...")
    
    try:
        import time
        
        # Test intent recognition speed
        from core.intent import IntentRecognizer
        intent_recognizer = IntentRecognizer()
        
        start_time = time.time()
        for i in range(10):
            intent_recognizer.recognize("Hello, how are you?", "en")
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"✅ Intent recognition speed: {avg_time:.3f}s per recognition")
        
        # Test memory operations
        from core.memory import MemoryManager
        memory = MemoryManager()
        
        start_time = time.time()
        for i in range(10):
            memory.get_conversation_history(limit=5)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"✅ Memory operations speed: {avg_time:.3f}s per operation")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🤖 Robot Brain System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Core Modules", test_core_modules),
        ("Speech System", test_speech_system),
        ("Vision System", test_vision_system),
        ("AI System", test_ai_system),
        ("UI System", test_ui_system),
        ("Action Modules", test_action_modules),
        ("System Integration", test_integration),
        ("Performance", run_performance_test),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())