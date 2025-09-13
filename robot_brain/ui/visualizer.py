"""
🎵 Spectrum Visualizer

Real-time audio spectrum visualization synchronized with speech output.
Provides visual feedback during robot speech.
"""

import pygame
import numpy as np
import time
import threading
from typing import List, Optional, Callable
from collections import deque

class SpectrumVisualizer:
    """
    🎵 Audio Spectrum Visualizer
    
    Provides real-time audio spectrum visualization synchronized with speech.
    Creates engaging visual feedback during robot speech output.
    """
    
    def __init__(self, width: int = 800, height: int = 200):
        """
        Initialize spectrum visualizer.
        
        Args:
            width: Visualizer width
            height: Visualizer height
        """
        self.width = width
        self.height = height
        
        # Visual settings
        self.background_color = (10, 10, 20)  # Very dark blue
        self.bar_color = (0, 150, 255)        # Blue
        self.peak_color = (255, 255, 255)     # White
        self.glow_color = (100, 200, 255)     # Light blue
        
        # Spectrum settings
        self.num_bars = 32
        self.bar_width = self.width // self.num_bars
        self.max_bar_height = self.height - 20
        
        # Animation settings
        self.smoothing_factor = 0.8
        self.peak_decay = 0.95
        self.animation_speed = 0.1
        
        # Data storage
        self.spectrum_data = deque(maxlen=self.num_bars)
        self.peak_data = deque(maxlen=self.num_bars)
        self.current_spectrum = [0.0] * self.num_bars
        self.current_peaks = [0.0] * self.num_bars
        
        # Animation state
        self.is_active = False
        self.animation_thread = None
        self.update_callback = None
        
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Create surface for visualization
        self.surface = pygame.Surface((self.width, self.height))
        
        print("✅ Spectrum visualizer initialized")
    
    def start_visualization(self, callback: Callable = None):
        """
        Start spectrum visualization.
        
        Args:
            callback: Function to call with visualization surface
        """
        if self.is_active:
            return
        
        self.is_active = True
        self.update_callback = callback
        
        # Start animation thread
        self.animation_thread = threading.Thread(
            target=self._animation_loop,
            daemon=True
        )
        self.animation_thread.start()
        
        print("🎵 Spectrum visualization started")
    
    def stop_visualization(self):
        """Stop spectrum visualization."""
        self.is_active = False
        
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
        
        print("⏹️ Spectrum visualization stopped")
    
    def update_spectrum(self, spectrum_data: List[float]):
        """
        Update spectrum data.
        
        Args:
            spectrum_data: New spectrum data (frequency bins)
        """
        if not self.is_active:
            return
        
        try:
            # Normalize and scale spectrum data
            if len(spectrum_data) > 0:
                # Convert to numpy array for easier processing
                spectrum = np.array(spectrum_data)
                
                # Normalize to 0-1 range
                if np.max(spectrum) > 0:
                    spectrum = spectrum / np.max(spectrum)
                
                # Resample to match number of bars
                if len(spectrum) != self.num_bars:
                    # Simple resampling - take every nth sample or interpolate
                    if len(spectrum) > self.num_bars:
                        # Downsample
                        step = len(spectrum) // self.num_bars
                        spectrum = spectrum[::step][:self.num_bars]
                    else:
                        # Upsample by repeating
                        spectrum = np.repeat(spectrum, self.num_bars // len(spectrum) + 1)[:self.num_bars]
                
                # Apply smoothing
                for i in range(self.num_bars):
                    self.current_spectrum[i] = (
                        self.current_spectrum[i] * self.smoothing_factor +
                        spectrum[i] * (1 - self.smoothing_factor)
                    )
                    
                    # Update peaks
                    if spectrum[i] > self.current_peaks[i]:
                        self.current_peaks[i] = spectrum[i]
                    else:
                        self.current_peaks[i] *= self.peak_decay
                
                # Store data
                self.spectrum_data.append(list(self.current_spectrum))
                self.peak_data.append(list(self.current_peaks))
            
        except Exception as e:
            print(f"❌ Spectrum update error: {e}")
    
    def _animation_loop(self):
        """Main animation loop."""
        try:
            while self.is_active:
                # Render visualization
                self._render_spectrum()
                
                # Call update callback if provided
                if self.update_callback:
                    self.update_callback(self.surface)
                
                # Control animation speed
                time.sleep(self.animation_speed)
                
        except Exception as e:
            print(f"❌ Animation loop error: {e}")
        finally:
            self.is_active = False
    
    def _render_spectrum(self):
        """Render spectrum visualization."""
        try:
            # Clear surface
            self.surface.fill(self.background_color)
            
            # Draw spectrum bars
            for i in range(self.num_bars):
                bar_height = int(self.current_spectrum[i] * self.max_bar_height)
                peak_height = int(self.current_peaks[i] * self.max_bar_height)
                
                x = i * self.bar_width
                
                # Draw main bar
                if bar_height > 0:
                    bar_rect = pygame.Rect(x, self.height - bar_height, self.bar_width - 2, bar_height)
                    pygame.draw.rect(self.surface, self.bar_color, bar_rect)
                    
                    # Add glow effect
                    glow_rect = pygame.Rect(x - 1, self.height - bar_height - 1, 
                                          self.bar_width, bar_height + 2)
                    pygame.draw.rect(self.surface, self.glow_color, glow_rect, 1)
                
                # Draw peak indicator
                if peak_height > 0:
                    peak_y = self.height - peak_height
                    pygame.draw.line(self.surface, self.peak_color, 
                                   (x, peak_y), (x + self.bar_width - 2, peak_y), 2)
            
            # Draw center line
            center_y = self.height // 2
            pygame.draw.line(self.surface, (50, 50, 50), (0, center_y), (self.width, center_y), 1)
            
        except Exception as e:
            print(f"❌ Spectrum rendering error: {e}")
    
    def render_to_surface(self, target_surface: pygame.Surface, position: tuple = (0, 0)):
        """
        Render visualization to a target surface.
        
        Args:
            target_surface: Target pygame surface
            position: Position to render at (x, y)
        """
        try:
            target_surface.blit(self.surface, position)
        except Exception as e:
            print(f"❌ Surface rendering error: {e}")
    
    def get_visualization_surface(self) -> pygame.Surface:
        """Get current visualization surface."""
        return self.surface
    
    def set_visual_style(self, style: str = "default"):
        """
        Set visual style for the spectrum.
        
        Args:
            style: Style name ('default', 'neon', 'minimal', 'colorful')
        """
        try:
            if style == "neon":
                self.background_color = (0, 0, 0)
                self.bar_color = (0, 255, 100)
                self.peak_color = (255, 255, 255)
                self.glow_color = (0, 200, 150)
            elif style == "minimal":
                self.background_color = (30, 30, 30)
                self.bar_color = (200, 200, 200)
                self.peak_color = (255, 255, 255)
                self.glow_color = (150, 150, 150)
            elif style == "colorful":
                self.background_color = (20, 10, 30)
                self.bar_color = (255, 100, 200)
                self.peak_color = (255, 255, 100)
                self.glow_color = (200, 150, 255)
            else:  # default
                self.background_color = (10, 10, 20)
                self.bar_color = (0, 150, 255)
                self.peak_color = (255, 255, 255)
                self.glow_color = (100, 200, 255)
            
            print(f"✅ Visual style set to: {style}")
            
        except Exception as e:
            print(f"❌ Style setting error: {e}")
    
    def set_animation_speed(self, speed: float):
        """
        Set animation speed.
        
        Args:
            speed: Animation speed (0.01 = very fast, 0.1 = normal, 0.5 = slow)
        """
        self.animation_speed = max(0.01, min(1.0, speed))
        print(f"✅ Animation speed set to: {self.animation_speed}")
    
    def set_smoothing(self, factor: float):
        """
        Set smoothing factor for spectrum data.
        
        Args:
            factor: Smoothing factor (0.0 = no smoothing, 1.0 = maximum smoothing)
        """
        self.smoothing_factor = max(0.0, min(1.0, factor))
        print(f"✅ Smoothing factor set to: {self.smoothing_factor}")
    
    def generate_test_spectrum(self) -> List[float]:
        """Generate test spectrum data for demonstration."""
        import math
        
        # Generate sine wave pattern
        time_val = time.time()
        spectrum = []
        
        for i in range(self.num_bars):
            # Create multiple sine waves for interesting pattern
            freq1 = math.sin(time_val * 2 + i * 0.2) * 0.5
            freq2 = math.sin(time_val * 3 + i * 0.1) * 0.3
            freq3 = math.sin(time_val * 1.5 + i * 0.3) * 0.2
            
            value = abs(freq1 + freq2 + freq3)
            spectrum.append(value)
        
        return spectrum
    
    def test_visualization(self, duration: float = 5.0) -> bool:
        """
        Test visualization with generated data.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if test successful
        """
        try:
            print("🧪 Testing spectrum visualization...")
            
            # Start visualization
            self.start_visualization()
            
            # Generate test data
            start_time = time.time()
            while time.time() - start_time < duration:
                test_spectrum = self.generate_test_spectrum()
                self.update_spectrum(test_spectrum)
                time.sleep(0.1)
            
            # Stop visualization
            self.stop_visualization()
            
            print("✅ Spectrum visualization test successful")
            return True
            
        except Exception as e:
            print(f"❌ Spectrum visualization test error: {e}")
            return False
    
    def get_visualizer_info(self) -> dict:
        """Get visualizer information."""
        return {
            'width': self.width,
            'height': self.height,
            'num_bars': self.num_bars,
            'is_active': self.is_active,
            'animation_speed': self.animation_speed,
            'smoothing_factor': self.smoothing_factor,
            'current_spectrum': self.current_spectrum.copy(),
            'current_peaks': self.current_peaks.copy()
        }
    
    def cleanup(self):
        """Clean up visualizer resources."""
        try:
            self.stop_visualization()
            print("🧹 Spectrum visualizer cleaned up")
        except Exception as e:
            print(f"❌ Visualizer cleanup error: {e}")