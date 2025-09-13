#!/usr/bin/env python3
"""
🚀 Robot Brain Quick Start

A simplified version of the robot brain for quick testing and demonstration.
This script provides basic functionality without all the advanced features.
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def quick_demo():
    """Run a quick demonstration of the robot brain."""
    print("🤖 Robot Brain Quick Start Demo")
    print("=" * 40)
    
    try:
        # Import core modules
        from core.intent import IntentRecognizer
        from core.memory import MemoryManager
        from actions.entertainment import EntertainmentModule
        
        print("✅ Core modules loaded")
        
        # Initialize components
        intent_recognizer = IntentRecognizer()
        memory = MemoryManager()
        entertainment = EntertainmentModule()
        
        print("✅ Components initialized")
        
        # Test intent recognition
        print("\n🧪 Testing Intent Recognition:")
        
        test_phrases = [
            ("Hello, how are you?", "en"),
            ("আসসালামু আলাইকুম", "bn"),
            ("Tell me a joke", "en"),
            ("কৌতুক বলো", "bn"),
            ("Take a picture", "en"),
            ("ছবি তুলো", "bn")
        ]
        
        for phrase, language in test_phrases:
            intent = intent_recognizer.recognize(phrase, language)
            print(f"  '{phrase}' -> {intent.type.value} (confidence: {intent.confidence:.2f})")
        
        # Test entertainment
        print("\n🎭 Testing Entertainment:")
        
        bangla_joke = entertainment.get_joke("bn")
        print(f"Bangla: {bangla_joke[:100]}...")
        
        english_joke = entertainment.get_joke("en")
        print(f"English: {english_joke[:100]}...")
        
        # Test memory
        print("\n🧠 Testing Memory:")
        
        stats = memory.get_memory_stats()
        print(f"Memory stats: {stats}")
        
        print("\n✅ Quick demo completed successfully!")
        print("\nTo run the full system:")
        print("  python3 main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_demo():
    """Run an interactive demonstration."""
    print("\n🎮 Interactive Demo")
    print("Type 'quit' to exit")
    print("=" * 30)
    
    try:
        from core.intent import IntentRecognizer
        from actions.entertainment import EntertainmentModule
        
        intent_recognizer = IntentRecognizer()
        entertainment = EntertainmentModule()
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Detect language (simple heuristic)
            language = 'bn' if any('\u0980' <= char <= '\u09FF' for char in user_input) else 'en'
            
            # Recognize intent
            intent = intent_recognizer.recognize(user_input, language)
            print(f"Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
            
            # Generate response based on intent
            if intent.type.value == "entertainment":
                if language == 'bn':
                    response = entertainment.get_joke("bn")
                else:
                    response = entertainment.get_joke("en")
                print(f"Robot: {response}")
            
            elif intent.type.value == "greeting":
                if language == 'bn':
                    response = "আসসালামু আলাইকুম! আমি আপনার রোবট সহকারী।"
                else:
                    response = "Hello! I'm your robot assistant."
                print(f"Robot: {response}")
            
            elif intent.type.value == "question":
                if language == 'bn':
                    response = "এটি একটি ভালো প্রশ্ন। আমি আপনাকে সাহায্য করতে পারি।"
                else:
                    response = "That's a good question. I can help you with that."
                print(f"Robot: {response}")
            
            else:
                if language == 'bn':
                    response = "দুঃখিত, আমি বুঝতে পারিনি। আবার বলুন দয়া করে।"
                else:
                    response = "Sorry, I didn't understand. Please try again."
                print(f"Robot: {response}")
    
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Interactive demo error: {e}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        quick_demo()

if __name__ == "__main__":
    main()