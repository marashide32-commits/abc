"""
🗣️ Bangla Text-to-Speech System

High-quality Bangla speech synthesis using Coqui TTS with mobassir94's model.
Provides natural-sounding Bangla voice output for the robot.
"""

import os
import tempfile
import threading
from pathlib import Path
from typing import Optional, Callable
import numpy as np

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ Coqui TTS not available. Install with: pip install TTS")

class BanglaTTS:
    """
    🇧🇩 Bangla Text-to-Speech Engine
    
    Uses Coqui TTS with mobassir94's Bangla model for high-quality speech synthesis.
    Provides natural-sounding Bangla voice output.
    """
    
    def __init__(self, model_name: str = "mobassir94/bangla-tts"):
        """
        Initialize Bangla TTS system.
        
        Args:
            model_name: Name of the TTS model to use
        """
        self.model_name = model_name
        self.model = None
        self.is_initialized = False
        self.audio_cache = {}
        
        # Audio settings
        self.sample_rate = 22050
        self.output_format = "wav"
        
        if TTS_AVAILABLE:
            self._initialize_model()
        else:
            print("❌ Coqui TTS not available. Bangla TTS will not work.")
    
    def _initialize_model(self):
        """Initialize the TTS model."""
        try:
            print("🗣️ Initializing Bangla TTS model...")
            
            # Load the model
            self.model = TTS(model_name=self.model_name)
            self.is_initialized = True
            
            print("✅ Bangla TTS model loaded successfully")
            
        except Exception as e:
            print(f"❌ Bangla TTS initialization error: {e}")
            self.is_initialized = False
    
    def synthesize(self, text: str, output_path: str = None, 
                   callback: Callable = None) -> Optional[str]:
        """
        Synthesize Bangla text to speech.
        
        Args:
            text: Bangla text to synthesize
            output_path: Path to save audio file (optional)
            callback: Callback function for progress updates
            
        Returns:
            Path to generated audio file or None if failed
        """
        if not self.is_initialized or not self.model:
            print("❌ Bangla TTS not initialized")
            return None
        
        if not text or not text.strip():
            print("⚠️ Empty text provided for synthesis")
            return None
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if callback:
                callback("Processing Bangla text...")
            
            # Check cache first
            cache_key = hash(cleaned_text)
            if cache_key in self.audio_cache:
                cached_path = self.audio_cache[cache_key]
                if Path(cached_path).exists():
                    if callback:
                        callback("Using cached audio")
                    return cached_path
            
            # Generate output path if not provided
            if not output_path:
                output_path = self._get_temp_audio_path()
            
            if callback:
                callback("Generating Bangla speech...")
            
            # Synthesize speech
            self.model.tts_to_file(
                text=cleaned_text,
                file_path=output_path
            )
            
            # Cache the result
            self.audio_cache[cache_key] = output_path
            
            if callback:
                callback("Bangla speech generated successfully")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Bangla TTS synthesis error: {e}")
            if callback:
                callback(f"Error: {str(e)}")
            return None
    
    def synthesize_async(self, text: str, callback: Callable, 
                        output_path: str = None):
        """
        Synthesize speech asynchronously.
        
        Args:
            text: Text to synthesize
            callback: Callback function with (success, audio_path, error)
            output_path: Path to save audio file
        """
        def async_synthesis():
            try:
                audio_path = self.synthesize(text, output_path)
                if audio_path:
                    callback(True, audio_path, None)
                else:
                    callback(False, None, "Synthesis failed")
            except Exception as e:
                callback(False, None, str(e))
        
        thread = threading.Thread(target=async_synthesis, daemon=True)
        thread.start()
        return thread
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for synthesis.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text suitable for TTS
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Handle common Bangla text issues
        replacements = {
            # Remove English words that might cause issues
            "robot": "রোবট",
            "hello": "হ্যালো",
            "sorry": "দুঃখিত",
            "thank you": "ধন্যবাদ",
            "please": "দয়া করে",
            "yes": "হ্যাঁ",
            "no": "না",
            "okay": "ঠিক আছে",
            "good": "ভালো",
            "bad": "খারাপ"
        }
        
        for eng, bangla in replacements.items():
            text = text.replace(eng, bangla)
        
        # Remove special characters that might cause issues
        import re
        text = re.sub(r'[^\u0980-\u09FF\u0020\u002E\u002C\u003F\u0021]', '', text)
        
        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _get_temp_audio_path(self) -> str:
        """Generate temporary audio file path."""
        temp_dir = Path(tempfile.gettempdir()) / "robot_brain" / "bangla_tts"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        import time
        timestamp = int(time.time() * 1000)
        return str(temp_dir / f"bangla_speech_{timestamp}.{self.output_format}")
    
    def get_available_voices(self) -> list:
        """Get list of available voices/models."""
        if not self.is_initialized:
            return []
        
        try:
            # Get available models from TTS
            available_models = TTS.list_models()
            bangla_models = [model for model in available_models if 'bangla' in model.lower()]
            return bangla_models
        except:
            return [self.model_name]
    
    def set_voice(self, voice_name: str) -> bool:
        """
        Change the voice/model used for synthesis.
        
        Args:
            voice_name: Name of the voice/model to use
            
        Returns:
            True if voice changed successfully
        """
        try:
            if not TTS_AVAILABLE:
                return False
            
            print(f"🗣️ Changing Bangla TTS voice to: {voice_name}")
            
            # Load new model
            self.model = TTS(model_name=voice_name)
            self.model_name = voice_name
            self.is_initialized = True
            
            # Clear cache since voice changed
            self.audio_cache.clear()
            
            print("✅ Bangla TTS voice changed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to change Bangla TTS voice: {e}")
            return False
    
    def get_synthesis_info(self) -> dict:
        """Get information about the current TTS setup."""
        return {
            'model_name': self.model_name,
            'is_initialized': self.is_initialized,
            'sample_rate': self.sample_rate,
            'output_format': self.output_format,
            'cache_size': len(self.audio_cache),
            'tts_available': TTS_AVAILABLE
        }
    
    def clear_cache(self):
        """Clear the audio cache."""
        # Remove cached files
        for cache_path in self.audio_cache.values():
            try:
                if Path(cache_path).exists():
                    Path(cache_path).unlink()
            except:
                pass
        
        self.audio_cache.clear()
        print("🗑️ Bangla TTS cache cleared")
    
    def test_synthesis(self, test_text: str = "আসসালামু আলাইকুম") -> bool:
        """
        Test the TTS system with sample text.
        
        Args:
            test_text: Text to use for testing
            
        Returns:
            True if test successful
        """
        try:
            print(f"🧪 Testing Bangla TTS with: '{test_text}'")
            
            audio_path = self.synthesize(test_text)
            
            if audio_path and Path(audio_path).exists():
                print("✅ Bangla TTS test successful")
                return True
            else:
                print("❌ Bangla TTS test failed")
                return False
                
        except Exception as e:
            print(f"❌ Bangla TTS test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        self.clear_cache()
        self.model = None
        self.is_initialized = False