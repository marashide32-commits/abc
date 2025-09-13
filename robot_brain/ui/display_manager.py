"""
🖥️ Display Manager

Manages the robot's display output including text, images, and status information.
Provides a user-friendly interface for the robot's screen.
"""

import pygame
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

class DisplayManager:
    """
    🖥️ Display Manager
    
    Manages the robot's display output including text, images, and status.
    Provides a user-friendly interface for the robot's screen.
    """
    
    def __init__(self, width: int = 800, height: int = 480):
        """
        Initialize display manager.
        
        Args:
            width: Display width
            height: Display height
        """
        from ..core.config import config
        
        self.width = width or config.DISPLAY_WIDTH
        self.height = height or config.DISPLAY_HEIGHT
        
        # Display settings
        self.background_color = (20, 20, 30)  # Dark blue-gray
        self.text_color = (255, 255, 255)     # White
        self.accent_color = (0, 150, 255)     # Blue
        self.warning_color = (255, 165, 0)    # Orange
        self.error_color = (255, 50, 50)      # Red
        
        # Font settings
        self.font_size = config.FONT_SIZE
        self.title_font_size = int(self.font_size * 1.5)
        self.small_font_size = int(self.font_size * 0.8)
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Robot Brain Display")
        
        # Load fonts
        self.fonts = self._load_fonts()
        
        # Display state
        self.current_text = ""
        self.current_image = None
        self.status_message = ""
        self.is_speaking = False
        self.last_update = time.time()
        
        # Animation settings
        self.text_animation_speed = 0.05  # seconds per character
        self.animation_thread = None
        self.animation_running = False
        
        print("✅ Display manager initialized")
    
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Load fonts for different text sizes."""
        try:
            fonts = {}
            
            # Try to load system fonts
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "C:/Windows/Fonts/arial.ttf"       # Windows
            ]
            
            font_path = None
            for path in font_paths:
                if Path(path).exists():
                    font_path = path
                    break
            
            if font_path:
                fonts['regular'] = pygame.font.Font(font_path, self.font_size)
                fonts['title'] = pygame.font.Font(font_path, self.title_font_size)
                fonts['small'] = pygame.font.Font(font_path, self.small_font_size)
            else:
                # Use default font
                fonts['regular'] = pygame.font.Font(None, self.font_size)
                fonts['title'] = pygame.font.Font(None, self.title_font_size)
                fonts['small'] = pygame.font.Font(None, self.small_font_size)
            
            return fonts
            
        except Exception as e:
            print(f"❌ Font loading error: {e}")
            # Fallback to default fonts
            return {
                'regular': pygame.font.Font(None, self.font_size),
                'title': pygame.font.Font(None, self.title_font_size),
                'small': pygame.font.Font(None, self.small_font_size)
            }
    
    def show_text(self, text: str, animated: bool = True, duration: float = None):
        """
        Display text on screen.
        
        Args:
            text: Text to display
            animated: Whether to animate text appearance
            duration: How long to show text (None for permanent)
        """
        try:
            self.current_text = text
            
            if animated:
                self._animate_text(text)
            else:
                self._render_text(text)
            
            # Set duration if specified
            if duration:
                threading.Timer(duration, self.clear_text).start()
            
            self.last_update = time.time()
            
        except Exception as e:
            print(f"❌ Text display error: {e}")
    
    def _animate_text(self, text: str):
        """Animate text appearance character by character."""
        if self.animation_running:
            self.animation_running = False
            if self.animation_thread:
                self.animation_thread.join(timeout=0.1)
        
        self.animation_running = True
        self.animation_thread = threading.Thread(
            target=self._text_animation_worker,
            args=(text,),
            daemon=True
        )
        self.animation_thread.start()
    
    def _text_animation_worker(self, full_text: str):
        """Worker thread for text animation."""
        try:
            for i in range(len(full_text) + 1):
                if not self.animation_running:
                    break
                
                partial_text = full_text[:i]
                self._render_text(partial_text)
                time.sleep(self.text_animation_speed)
            
            self.animation_running = False
            
        except Exception as e:
            print(f"❌ Text animation error: {e}")
            self.animation_running = False
    
    def _render_text(self, text: str):
        """Render text on screen."""
        try:
            # Clear screen
            self.screen.fill(self.background_color)
            
            # Split text into lines
            lines = self._wrap_text(text, self.width - 40)
            
            # Calculate starting position (centered)
            total_height = len(lines) * (self.font_size + 5)
            start_y = (self.height - total_height) // 2
            
            # Render each line
            for i, line in enumerate(lines):
                text_surface = self.fonts['regular'].render(line, True, self.text_color)
                text_rect = text_surface.get_rect(center=(self.width // 2, start_y + i * (self.font_size + 5)))
                self.screen.blit(text_surface, text_rect)
            
            # Show status if available
            if self.status_message:
                self._render_status()
            
            # Show speaking indicator
            if self.is_speaking:
                self._render_speaking_indicator()
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            print(f"❌ Text rendering error: {e}")
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        try:
            words = text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                # Test if adding this word exceeds width
                test_line = ' '.join(current_line + [word])
                text_surface = self.fonts['regular'].render(test_line, True, self.text_color)
                
                if text_surface.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Word is too long, add it anyway
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
            
        except Exception as e:
            print(f"❌ Text wrapping error: {e}")
            return [text]
    
    def show_image(self, image_path: str, caption: str = None):
        """
        Display an image on screen.
        
        Args:
            image_path: Path to image file
            caption: Optional caption text
        """
        try:
            if not Path(image_path).exists():
                print(f"❌ Image not found: {image_path}")
                return
            
            # Load image
            image = pygame.image.load(image_path)
            
            # Scale image to fit screen
            image_rect = image.get_rect()
            scale_factor = min(
                (self.width - 40) / image_rect.width,
                (self.height - 100) / image_rect.height
            )
            
            new_width = int(image_rect.width * scale_factor)
            new_height = int(image_rect.height * scale_factor)
            
            image = pygame.transform.scale(image, (new_width, new_height))
            
            # Clear screen
            self.screen.fill(self.background_color)
            
            # Center image
            image_rect = image.get_rect(center=(self.width // 2, self.height // 2 - 20))
            self.screen.blit(image, image_rect)
            
            # Show caption if provided
            if caption:
                caption_surface = self.fonts['small'].render(caption, True, self.text_color)
                caption_rect = caption_surface.get_rect(center=(self.width // 2, self.height - 30))
                self.screen.blit(caption_surface, caption_rect)
            
            # Update display
            pygame.display.flip()
            
            self.current_image = image_path
            self.last_update = time.time()
            
        except Exception as e:
            print(f"❌ Image display error: {e}")
    
    def show_status(self, message: str, status_type: str = "info"):
        """
        Show status message.
        
        Args:
            message: Status message
            status_type: Type of status (info, warning, error)
        """
        self.status_message = message
        self.status_type = status_type
        self._render_status()
    
    def _render_status(self):
        """Render status message."""
        try:
            if not self.status_message:
                return
            
            # Choose color based on status type
            color_map = {
                'info': self.accent_color,
                'warning': self.warning_color,
                'error': self.error_color
            }
            color = color_map.get(self.status_type, self.text_color)
            
            # Render status text
            status_surface = self.fonts['small'].render(self.status_message, True, color)
            status_rect = status_surface.get_rect(bottomleft=(10, self.height - 10))
            self.screen.blit(status_surface, status_rect)
            
        except Exception as e:
            print(f"❌ Status rendering error: {e}")
    
    def set_speaking(self, is_speaking: bool):
        """Set speaking indicator."""
        self.is_speaking = is_speaking
        if not self.animation_running:
            self._render_text(self.current_text)
    
    def _render_speaking_indicator(self):
        """Render speaking indicator."""
        try:
            # Draw animated dots
            current_time = time.time()
            dot_count = int((current_time * 3) % 4)  # 0-3 dots
            
            for i in range(dot_count):
                x = self.width - 30 - (i * 10)
                y = self.height - 30
                pygame.draw.circle(self.screen, self.accent_color, (x, y), 3)
            
        except Exception as e:
            print(f"❌ Speaking indicator error: {e}")
    
    def show_welcome_screen(self):
        """Show welcome screen with robot information."""
        try:
            welcome_text = [
                "🤖 Robot Brain Active",
                "",
                "আসসালামু আলাইকুম!",
                "Hello! I'm your robot assistant.",
                "",
                "I can:",
                "• Recognize faces",
                "• Answer questions",
                "• Take photos",
                "• Speak Bangla & English",
                "",
                "Ready to help! 🚀"
            ]
            
            self.show_text('\n'.join(welcome_text), animated=True)
            
        except Exception as e:
            print(f"❌ Welcome screen error: {e}")
    
    def show_face_recognition_screen(self, person_name: str, confidence: float):
        """Show face recognition result."""
        try:
            if person_name == "Unknown":
                text = "👤 Unknown Person Detected"
            else:
                text = f"👋 Welcome, {person_name}!\n\nConfidence: {confidence:.1%}"
            
            self.show_text(text, animated=True, duration=3.0)
            
        except Exception as e:
            print(f"❌ Face recognition screen error: {e}")
    
    def show_loading_screen(self, message: str = "Processing..."):
        """Show loading screen with animated dots."""
        try:
            def loading_animation():
                dots = ""
                while True:
                    for i in range(4):
                        loading_text = f"{message}{dots}"
                        self._render_text(loading_text)
                        time.sleep(0.5)
                        dots += "."
                        if len(dots) > 3:
                            dots = ""
            
            # Start loading animation in background
            threading.Thread(target=loading_animation, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Loading screen error: {e}")
    
    def clear_text(self):
        """Clear current text display."""
        self.current_text = ""
        self.screen.fill(self.background_color)
        pygame.display.flip()
    
    def clear_status(self):
        """Clear status message."""
        self.status_message = ""
        if not self.animation_running:
            self._render_text(self.current_text)
    
    def update_status(self):
        """Update display status (called periodically)."""
        try:
            # Check if display needs refresh
            if time.time() - self.last_update > 1.0:
                if not self.animation_running:
                    self._render_text(self.current_text)
            
        except Exception as e:
            print(f"❌ Status update error: {e}")
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information."""
        return {
            'width': self.width,
            'height': self.height,
            'current_text': self.current_text,
            'current_image': self.current_image,
            'status_message': self.status_message,
            'is_speaking': self.is_speaking,
            'animation_running': self.animation_running,
            'fonts_loaded': len(self.fonts)
        }
    
    def test_display(self) -> bool:
        """Test display functionality."""
        try:
            print("🧪 Testing display...")
            
            # Test text display
            self.show_text("Display Test\n\nThis is a test message.", animated=True)
            time.sleep(2)
            
            # Test status
            self.show_status("Test status message", "info")
            time.sleep(1)
            
            # Test speaking indicator
            self.set_speaking(True)
            time.sleep(1)
            self.set_speaking(False)
            
            print("✅ Display test successful")
            return True
            
        except Exception as e:
            print(f"❌ Display test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up display resources."""
        try:
            self.animation_running = False
            if self.animation_thread:
                self.animation_thread.join(timeout=1.0)
            
            pygame.quit()
            print("🧹 Display manager cleaned up")
            
        except Exception as e:
            print(f"❌ Display cleanup error: {e}")