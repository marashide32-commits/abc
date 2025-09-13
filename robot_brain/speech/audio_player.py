"""
🔊 Audio Player with Spectrum Visualization

Handles audio playback with real-time spectrum visualization.
Coordinates with the visualizer for synchronized audio-visual output.
"""

import os
import time
import threading
import numpy as np
from pathlib import Path
from typing import Optional, Callable, List
import pygame
import librosa

try:
    import pyaudio
    import struct
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available. Audio playback may be limited.")

class AudioPlayer:
    """
    🎵 Audio Player with Spectrum Visualization
    
    Plays audio files with real-time spectrum analysis and visualization.
    Provides synchronized audio-visual feedback for the robot's speech.
    """
    
    def __init__(self):
        """Initialize audio player system."""
        self.is_playing = False
        self.current_audio = None
        self.spectrum_data = []
        self.visualizer_callback = None
        
        # Audio settings
        self.sample_rate = 22050
        self.chunk_size = 1024
        self.channels = 1
        
        # Initialize pygame mixer for simple playback
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=self.channels)
        
        # Initialize PyAudio for spectrum analysis
        self.audio = None
        self.stream = None
        if PYAUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except:
                self.audio = None
    
    def play_with_visualizer(self, audio_path: str, visualizer, 
                           callback: Callable = None) -> bool:
        """
        Play audio file with spectrum visualization.
        
        Args:
            audio_path: Path to audio file
            visualizer: Visualizer object for spectrum display
            callback: Callback function for playback events
            
        Returns:
            True if playback started successfully
        """
        if not Path(audio_path).exists():
            print(f"❌ Audio file not found: {audio_path}")
            return False
        
        try:
            # Set up visualizer callback
            self.visualizer_callback = visualizer.update_spectrum if visualizer else None
            
            # Start playback in separate thread
            thread = threading.Thread(
                target=self._play_audio_with_spectrum,
                args=(audio_path, callback),
                daemon=True
            )
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False
    
    def _play_audio_with_spectrum(self, audio_path: str, callback: Callable = None):
        """
        Internal method to play audio with spectrum analysis.
        
        Args:
            audio_path: Path to audio file
            callback: Callback function for events
        """
        try:
            self.is_playing = True
            self.current_audio = audio_path
            
            if callback:
                callback("started", audio_path)
            
            # Load audio file
            audio_data, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Calculate spectrum data
            self._calculate_spectrum_data(audio_data)
            
            # Play audio using pygame
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Update visualizer while playing
            self._update_visualizer_during_playback()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            if callback:
                callback("completed", audio_path)
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            if callback:
                callback("error", str(e))
        
        finally:
            self.is_playing = False
            self.current_audio = None
    
    def _calculate_spectrum_data(self, audio_data: np.ndarray):
        """
        Calculate spectrum data for visualization.
        
        Args:
            audio_data: Audio data array
        """
        try:
            # Calculate spectrogram
            hop_length = 512
            n_fft = 2048
            
            # Compute short-time Fourier transform
            stft = librosa.stft(audio_data, hop_length=hop_length, n_fft=n_fft)
            magnitude = np.abs(stft)
            
            # Convert to dB scale
            magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
            
            # Store spectrum data
            self.spectrum_data = magnitude_db.T  # Transpose for time x frequency
            
        except Exception as e:
            print(f"❌ Spectrum calculation error: {e}")
            self.spectrum_data = []
    
    def _update_visualizer_during_playback(self):
        """Update visualizer during audio playback."""
        if not self.visualizer_callback or not self.spectrum_data.size:
            return
        
        try:
            # Calculate playback position
            total_frames = len(self.spectrum_data)
            frame_duration = 0.1  # Update every 100ms
            
            start_time = time.time()
            
            while self.is_playing and pygame.mixer.music.get_busy():
                # Calculate current frame
                elapsed = time.time() - start_time
                current_frame = int(elapsed / frame_duration)
                
                if current_frame < total_frames:
                    # Get spectrum data for current frame
                    spectrum_frame = self.spectrum_data[current_frame]
                    
                    # Update visualizer
                    self.visualizer_callback(spectrum_frame)
                
                time.sleep(frame_duration)
                
        except Exception as e:
            print(f"❌ Visualizer update error: {e}")
    
    def play_simple(self, audio_path: str, callback: Callable = None) -> bool:
        """
        Play audio file without spectrum visualization.
        
        Args:
            audio_path: Path to audio file
            callback: Callback function for events
            
        Returns:
            True if playback started successfully
        """
        if not Path(audio_path).exists():
            print(f"❌ Audio file not found: {audio_path}")
            return False
        
        try:
            def simple_playback():
                try:
                    self.is_playing = True
                    self.current_audio = audio_path
                    
                    if callback:
                        callback("started", audio_path)
                    
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    # Wait for completion
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    if callback:
                        callback("completed", audio_path)
                        
                except Exception as e:
                    if callback:
                        callback("error", str(e))
                finally:
                    self.is_playing = False
                    self.current_audio = None
            
            thread = threading.Thread(target=simple_playback, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Simple audio playback error: {e}")
            return False
    
    def stop(self):
        """Stop current audio playback."""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.current_audio = None
            print("⏹️ Audio playback stopped")
        except Exception as e:
            print(f"❌ Stop audio error: {e}")
    
    def pause(self):
        """Pause current audio playback."""
        try:
            pygame.mixer.music.pause()
            print("⏸️ Audio playback paused")
        except Exception as e:
            print(f"❌ Pause audio error: {e}")
    
    def resume(self):
        """Resume paused audio playback."""
        try:
            pygame.mixer.music.unpause()
            print("▶️ Audio playback resumed")
        except Exception as e:
            print(f"❌ Resume audio error: {e}")
    
    def set_volume(self, volume: float):
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
            pygame.mixer.music.set_volume(volume)
            print(f"🔊 Volume set to {volume:.1%}")
        except Exception as e:
            print(f"❌ Set volume error: {e}")
    
    def get_playback_info(self) -> dict:
        """Get current playback information."""
        return {
            'is_playing': self.is_playing,
            'current_audio': self.current_audio,
            'volume': pygame.mixer.music.get_volume(),
            'has_spectrum_data': len(self.spectrum_data) > 0,
            'pygame_available': True,
            'pyaudio_available': PYAUDIO_AVAILABLE
        }
    
    def test_audio_system(self) -> bool:
        """Test the audio system with a simple tone."""
        try:
            print("🧪 Testing audio system...")
            
            # Generate a simple test tone
            duration = 1.0  # seconds
            frequency = 440  # Hz (A note)
            
            # Generate sine wave
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit integers
            tone_int16 = (tone * 32767).astype(np.int16)
            
            # Save test tone
            test_path = Path(tempfile.gettempdir()) / "robot_brain" / "test_tone.wav"
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as WAV file
            import soundfile as sf
            sf.write(str(test_path), tone_int16, self.sample_rate)
            
            # Play test tone
            success = self.play_simple(str(test_path))
            
            if success:
                print("✅ Audio system test successful")
                # Clean up test file
                try:
                    test_path.unlink()
                except:
                    pass
                return True
            else:
                print("❌ Audio system test failed")
                return False
                
        except Exception as e:
            print(f"❌ Audio system test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            self.stop()
            pygame.mixer.quit()
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
            
            print("🧹 Audio player cleaned up")
            
        except Exception as e:
            print(f"❌ Audio cleanup error: {e}")