"""
🎤 Speech-to-Text System

Handles continuous speech recognition in both Bangla and English using Vosk.
Provides real-time transcription with language detection.
"""

import json
import pyaudio
import threading
import time
from typing import Tuple, Optional
from vosk import Model, KaldiRecognizer
from langdetect import detect, DetectorFactory
from pathlib import Path

# Set seed for consistent language detection
DetectorFactory.seed = 0

class SpeechToText:
    """
    🎙️ Speech-to-Text Engine
    
    Continuous speech recognition using Vosk with support for:
    - Bangla language recognition
    - English language recognition
    - Real-time transcription
    - Language auto-detection
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize STT system.
        
        Args:
            model_path: Path to Vosk model directory
        """
        from ..core.config import config
        
        self.model_path = model_path or config.VOSK_MODEL_PATH
        self.sample_rate = config.SAMPLE_RATE
        self.chunk_size = config.CHUNK_SIZE
        
        # Initialize Vosk model
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        
        # State management
        self.is_listening = False
        self.language_confidence_threshold = 0.8
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Vosk model and audio system."""
        try:
            print("🎤 Initializing Vosk STT model...")
            
            # Check if model exists
            if not Path(self.model_path).exists():
                raise FileNotFoundError(f"Vosk model not found at {self.model_path}")
            
            # Load Vosk model
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            # Initialize audio system
            self.audio = pyaudio.PyAudio()
            
            print("✅ STT model initialized successfully")
            
        except Exception as e:
            print(f"❌ STT initialization error: {e}")
            raise
    
    def listen(self, timeout: float = 5.0) -> Tuple[Optional[str], str]:
        """
        Listen for speech input and return transcribed text.
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            
        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        if not self.model or not self.recognizer:
            raise RuntimeError("STT model not initialized")
        
        try:
            # Start audio stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_listening = True
            print("👂 Listening for speech...")
            
            # Listen for speech
            start_time = time.time()
            audio_data = b''
            
            while self.is_listening and (time.time() - start_time) < timeout:
                try:
                    # Read audio data
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data += data
                    
                    # Process with Vosk
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").strip()
                        
                        if text:
                            # Detect language
                            language = self._detect_language(text)
                            print(f"👂 Heard: '{text}' (Language: {language})")
                            return text, language
                    
                    # Check for partial results
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "").strip()
                    
                    if partial_text and len(partial_text) > 3:
                        # Show partial results
                        print(f"👂 Partial: '{partial_text}'", end='\r')
                
                except Exception as e:
                    print(f"❌ Audio processing error: {e}")
                    break
            
            # Get final result if no complete result was found
            if not self.is_listening:
                final_result = json.loads(self.recognizer.FinalResult())
                text = final_result.get("text", "").strip()
                
                if text:
                    language = self._detect_language(text)
                    return text, language
            
            return None, "unknown"
            
        except Exception as e:
            print(f"❌ STT listening error: {e}")
            return None, "unknown"
        
        finally:
            self._cleanup_stream()
    
    def listen_continuous(self, callback, stop_event=None):
        """
        Listen continuously and call callback with results.
        
        Args:
            callback: Function to call with (text, language) results
            stop_event: Threading event to stop listening
        """
        def continuous_listener():
            while not (stop_event and stop_event.is_set()):
                try:
                    text, language = self.listen(timeout=1.0)
                    if text:
                        callback(text, language)
                except Exception as e:
                    print(f"❌ Continuous STT error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=continuous_listener, daemon=True)
        thread.start()
        return thread
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code ('bn' for Bangla, 'en' for English, 'unknown' for others)
        """
        if not text or len(text.strip()) < 2:
            return "unknown"
        
        try:
            # Use langdetect to identify language
            detected_lang = detect(text)
            
            # Map to our language codes
            if detected_lang == 'bn':
                return 'bn'
            elif detected_lang == 'en':
                return 'en'
            else:
                # Fallback: check for Bangla characters
                if self._contains_bangla_chars(text):
                    return 'bn'
                else:
                    return 'en'
                    
        except Exception as e:
            print(f"❌ Language detection error: {e}")
            # Fallback to character-based detection
            if self._contains_bangla_chars(text):
                return 'bn'
            else:
                return 'en'
    
    def _contains_bangla_chars(self, text: str) -> bool:
        """
        Check if text contains Bangla characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if Bangla characters found
        """
        # Bangla Unicode ranges
        bangla_ranges = [
            (0x0980, 0x09FF),  # Bengali
            (0x09BC, 0x09BD),  # Bengali
        ]
        
        for char in text:
            char_code = ord(char)
            for start, end in bangla_ranges:
                if start <= char_code <= end:
                    return True
        
        return False
    
    def _cleanup_stream(self):
        """Clean up audio stream resources."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
    
    def stop_listening(self):
        """Stop current listening session."""
        self.is_listening = False
        self._cleanup_stream()
    
    def cleanup(self):
        """Clean up all resources."""
        self.stop_listening()
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None
        
        self.model = None
        self.recognizer = None
    
    def get_audio_info(self) -> dict:
        """Get information about available audio devices."""
        if not self.audio:
            return {}
        
        info = {
            'default_input_device': self.audio.get_default_input_device_info(),
            'device_count': self.audio.get_device_count(),
            'devices': []
        }
        
        for i in range(info['device_count']):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    info['devices'].append(device_info)
            except:
                continue
        
        return info
    
    def test_microphone(self) -> bool:
        """Test if microphone is working properly."""
        try:
            # Try to open a test stream
            test_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Read a small amount of data
            test_stream.read(self.chunk_size, exception_on_overflow=False)
            
            test_stream.close()
            return True
            
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False