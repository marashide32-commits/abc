"""
🗣️ English Text-to-Speech System

High-quality English speech synthesis using Piper TTS.
Provides natural-sounding English voice output for the robot.
"""

import os
import tempfile
import threading
import subprocess
from pathlib import Path
from typing import Optional, Callable

class EnglishTTS:
    """
    🇺🇸 English Text-to-Speech Engine
    
    Uses Piper TTS for high-quality English speech synthesis.
    Provides natural-sounding English voice output.
    """
    
    def __init__(self, model_path: str = None, voice: str = "en_US-lessac-medium"):
        """
        Initialize English TTS system.
        
        Args:
            model_path: Path to Piper model directory
            voice: Voice model to use
        """
        from ..core.config import config
        
        self.voice = voice
        self.model_path = model_path or config.get_model_path("piper")
        self.is_initialized = False
        self.audio_cache = {}
        
        # Audio settings
        self.sample_rate = 22050
        self.output_format = "wav"
        
        self._check_piper_installation()
    
    def _check_piper_installation(self):
        """Check if Piper TTS is installed and available."""
        try:
            # Try to run piper command
            result = subprocess.run(['piper', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.is_initialized = True
                print("✅ Piper TTS is available")
            else:
                print("❌ Piper TTS not found. Please install Piper TTS.")
                self.is_initialized = False
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Piper TTS not found. Please install Piper TTS.")
            self.is_initialized = False
    
    def synthesize(self, text: str, output_path: str = None, 
                   callback: Callable = None) -> Optional[str]:
        """
        Synthesize English text to speech.
        
        Args:
            text: English text to synthesize
            output_path: Path to save audio file (optional)
            callback: Callback function for progress updates
            
        Returns:
            Path to generated audio file or None if failed
        """
        if not self.is_initialized:
            print("❌ English TTS not initialized")
            return None
        
        if not text or not text.strip():
            print("⚠️ Empty text provided for synthesis")
            return None
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if callback:
                callback("Processing English text...")
            
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
                callback("Generating English speech...")
            
            # Synthesize speech using Piper
            success = self._synthesize_with_piper(cleaned_text, output_path)
            
            if success:
                # Cache the result
                self.audio_cache[cache_key] = output_path
                
                if callback:
                    callback("English speech generated successfully")
                
                return output_path
            else:
                if callback:
                    callback("Failed to generate speech")
                return None
            
        except Exception as e:
            print(f"❌ English TTS synthesis error: {e}")
            if callback:
                callback(f"Error: {str(e)}")
            return None
    
    def _synthesize_with_piper(self, text: str, output_path: str) -> bool:
        """
        Synthesize speech using Piper TTS command line.
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare Piper command
            cmd = [
                'piper',
                '--model', f'{self.voice}.onnx',
                '--output_file', output_path
            ]
            
            # Run Piper with text input
            process = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if process.returncode == 0 and Path(output_path).exists():
                return True
            else:
                print(f"❌ Piper synthesis failed: {process.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Piper synthesis timeout")
            return False
        except Exception as e:
            print(f"❌ Piper synthesis error: {e}")
            return False
    
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
        
        # Handle common abbreviations
        replacements = {
            "Dr.": "Doctor",
            "Mr.": "Mister",
            "Mrs.": "Misses",
            "Ms.": "Miss",
            "Prof.": "Professor",
            "etc.": "etcetera",
            "vs.": "versus",
            "e.g.": "for example",
            "i.e.": "that is",
            "&": "and",
            "@": "at",
            "#": "hashtag",
            "%": "percent"
        }
        
        for abbrev, full in replacements.items():
            text = text.replace(abbrev, full)
        
        # Remove or replace special characters that might cause issues
        import re
        text = re.sub(r'[^\w\s\.\,\!\?\-\']', '', text)
        
        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _get_temp_audio_path(self) -> str:
        """Generate temporary audio file path."""
        temp_dir = Path(tempfile.gettempdir()) / "robot_brain" / "english_tts"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        import time
        timestamp = int(time.time() * 1000)
        return str(temp_dir / f"english_speech_{timestamp}.{self.output_format}")
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        try:
            # Try to list available models
            result = subprocess.run(['piper', '--list-models'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                voices = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Available'):
                        voices.append(line.strip())
                return voices
            else:
                return [self.voice]
                
        except:
            return [self.voice]
    
    def set_voice(self, voice_name: str) -> bool:
        """
        Change the voice used for synthesis.
        
        Args:
            voice_name: Name of the voice to use
            
        Returns:
            True if voice changed successfully
        """
        try:
            print(f"🗣️ Changing English TTS voice to: {voice_name}")
            
            # Check if voice is available
            available_voices = self.get_available_voices()
            if voice_name not in available_voices:
                print(f"❌ Voice '{voice_name}' not available")
                return False
            
            self.voice = voice_name
            
            # Clear cache since voice changed
            self.audio_cache.clear()
            
            print("✅ English TTS voice changed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to change English TTS voice: {e}")
            return False
    
    def get_synthesis_info(self) -> dict:
        """Get information about the current TTS setup."""
        return {
            'voice': self.voice,
            'is_initialized': self.is_initialized,
            'sample_rate': self.sample_rate,
            'output_format': self.output_format,
            'cache_size': len(self.audio_cache),
            'model_path': self.model_path
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
        print("🗑️ English TTS cache cleared")
    
    def test_synthesis(self, test_text: str = "Hello, I am your robot assistant") -> bool:
        """
        Test the TTS system with sample text.
        
        Args:
            test_text: Text to use for testing
            
        Returns:
            True if test successful
        """
        try:
            print(f"🧪 Testing English TTS with: '{test_text}'")
            
            audio_path = self.synthesize(test_text)
            
            if audio_path and Path(audio_path).exists():
                print("✅ English TTS test successful")
                return True
            else:
                print("❌ English TTS test failed")
                return False
                
        except Exception as e:
            print(f"❌ English TTS test error: {e}")
            return False
    
    def install_piper_voice(self, voice_name: str) -> bool:
        """
        Install a new Piper voice model.
        
        Args:
            voice_name: Name of the voice to install
            
        Returns:
            True if installation successful
        """
        try:
            print(f"📥 Installing Piper voice: {voice_name}")
            
            cmd = ['piper', '--download-voice', voice_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Voice '{voice_name}' installed successfully")
                return True
            else:
                print(f"❌ Failed to install voice: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Voice installation timeout")
            return False
        except Exception as e:
            print(f"❌ Voice installation error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        self.clear_cache()
        self.is_initialized = False