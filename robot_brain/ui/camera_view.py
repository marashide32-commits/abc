"""
📹 Camera View Display

Displays live camera feed with face recognition overlays.
Provides real-time visual feedback for the robot's vision system.
"""

import pygame
import cv2
import numpy as np
import time
import threading
from typing import Optional, Callable, Tuple, Dict, Any

class CameraView:
    """
    📹 Camera View Display
    
    Displays live camera feed with face recognition overlays.
    Provides real-time visual feedback for the robot's vision system.
    """
    
    def __init__(self, width: int = 640, height: int = 480):
        """
        Initialize camera view display.
        
        Args:
            width: Display width
            height: Display height
        """
        self.width = width
        self.height = height
        
        # Display settings
        self.background_color = (20, 20, 30)
        self.face_box_color = (0, 255, 0)      # Green for recognized faces
        self.unknown_face_color = (0, 0, 255)  # Red for unknown faces
        self.text_color = (255, 255, 255)      # White text
        self.text_background_color = (0, 0, 0, 128)  # Semi-transparent black
        
        # Font settings
        self.font_size = 20
        self.title_font_size = 24
        
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Create surface for camera view
        self.surface = pygame.Surface((self.width, self.height))
        
        # Load fonts
        self.fonts = self._load_fonts()
        
        # Display state
        self.current_frame = None
        self.face_annotations = []
        self.is_displaying = False
        self.display_thread = None
        
        # Camera feed settings
        self.fps = 30
        self.frame_delay = 1.0 / self.fps
        
        print("✅ Camera view display initialized")
    
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Load fonts for text rendering."""
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
                if path and pygame.font.get_fonts():
                    try:
                        font_path = path
                        break
                    except:
                        continue
            
            if font_path:
                fonts['regular'] = pygame.font.Font(font_path, self.font_size)
                fonts['title'] = pygame.font.Font(font_path, self.title_font_size)
            else:
                # Use default font
                fonts['regular'] = pygame.font.Font(None, self.font_size)
                fonts['title'] = pygame.font.Font(None, self.title_font_size)
            
            return fonts
            
        except Exception as e:
            print(f"❌ Font loading error: {e}")
            # Fallback to default fonts
            return {
                'regular': pygame.font.Font(None, self.font_size),
                'title': pygame.font.Font(None, self.title_font_size)
            }
    
    def start_display(self, camera_callback: Callable, update_callback: Callable = None):
        """
        Start camera view display.
        
        Args:
            camera_callback: Function to get camera frames
            update_callback: Function to call with rendered surface
        """
        if self.is_displaying:
            return
        
        self.is_displaying = True
        self.camera_callback = camera_callback
        self.update_callback = update_callback
        
        # Start display thread
        self.display_thread = threading.Thread(
            target=self._display_loop,
            daemon=True
        )
        self.display_thread.start()
        
        print("📹 Camera view display started")
    
    def stop_display(self):
        """Stop camera view display."""
        self.is_displaying = False
        
        if self.display_thread:
            self.display_thread.join(timeout=1.0)
        
        print("⏹️ Camera view display stopped")
    
    def update_frame(self, frame: np.ndarray, face_annotations: list = None):
        """
        Update camera frame and face annotations.
        
        Args:
            frame: Camera frame (OpenCV format)
            face_annotations: List of face annotation data
        """
        self.current_frame = frame
        self.face_annotations = face_annotations or []
    
    def _display_loop(self):
        """Main display loop."""
        try:
            while self.is_displaying:
                # Get camera frame
                if self.camera_callback:
                    frame = self.camera_callback()
                    if frame is not None:
                        self.current_frame = frame
                
                # Render frame
                if self.current_frame is not None:
                    self._render_frame()
                    
                    # Call update callback if provided
                    if self.update_callback:
                        self.update_callback(self.surface)
                
                # Control frame rate
                time.sleep(self.frame_delay)
                
        except Exception as e:
            print(f"❌ Display loop error: {e}")
        finally:
            self.is_displaying = False
    
    def _render_frame(self):
        """Render camera frame with annotations."""
        try:
            if self.current_frame is None:
                return
            
            # Convert OpenCV frame (BGR) to pygame surface (RGB)
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            
            # Scale frame to fit display size
            frame_surface = pygame.transform.scale(frame_surface, (self.width, self.height))
            
            # Clear surface and blit frame
            self.surface.fill(self.background_color)
            self.surface.blit(frame_surface, (0, 0))
            
            # Draw face annotations
            self._draw_face_annotations()
            
            # Draw status overlay
            self._draw_status_overlay()
            
        except Exception as e:
            print(f"❌ Frame rendering error: {e}")
    
    def _draw_face_annotations(self):
        """Draw face recognition annotations."""
        try:
            for annotation in self.face_annotations:
                if 'face_location' not in annotation:
                    continue
                
                x, y, w, h = annotation['face_location']
                name = annotation.get('name', 'Unknown')
                confidence = annotation.get('confidence', 0.0)
                role = annotation.get('role', '')
                
                # Choose color based on recognition status
                if name == 'Unknown':
                    color = self.unknown_face_color
                else:
                    color = self.face_box_color
                
                # Draw face rectangle
                pygame.draw.rect(self.surface, color, (x, y, w, h), 2)
                
                # Prepare label text
                if name == 'Unknown':
                    label = "Unknown Person"
                else:
                    label = f"{name}"
                    if role:
                        label += f" ({role})"
                    if confidence > 0:
                        label += f" {confidence:.1%}"
                
                # Draw label background
                text_surface = self.fonts['regular'].render(label, True, self.text_color)
                text_rect = text_surface.get_rect()
                
                # Position label above face
                label_x = x
                label_y = max(0, y - text_rect.height - 5)
                
                # Draw background rectangle
                bg_rect = pygame.Rect(label_x - 2, label_y - 2, 
                                    text_rect.width + 4, text_rect.height + 4)
                pygame.draw.rect(self.surface, self.text_background_color, bg_rect)
                
                # Draw text
                self.surface.blit(text_surface, (label_x, label_y))
                
        except Exception as e:
            print(f"❌ Face annotation drawing error: {e}")
    
    def _draw_status_overlay(self):
        """Draw status overlay on camera view."""
        try:
            # Draw title
            title_text = "Robot Vision System"
            title_surface = self.fonts['title'].render(title_text, True, self.text_color)
            self.surface.blit(title_surface, (10, 10))
            
            # Draw face count
            face_count = len(self.face_annotations)
            count_text = f"Faces detected: {face_count}"
            count_surface = self.fonts['regular'].render(count_text, True, self.text_color)
            self.surface.blit(count_surface, (10, 40))
            
            # Draw timestamp
            timestamp = time.strftime("%H:%M:%S")
            time_surface = self.fonts['regular'].render(timestamp, True, self.text_color)
            time_rect = time_surface.get_rect()
            self.surface.blit(time_surface, (self.width - time_rect.width - 10, 10))
            
            # Draw FPS indicator
            fps_text = f"FPS: {self.fps}"
            fps_surface = self.fonts['regular'].render(fps_text, True, self.text_color)
            fps_rect = fps_surface.get_rect()
            self.surface.blit(fps_surface, (self.width - fps_rect.width - 10, 40))
            
        except Exception as e:
            print(f"❌ Status overlay drawing error: {e}")
    
    def render_to_surface(self, target_surface: pygame.Surface, position: tuple = (0, 0)):
        """
        Render camera view to a target surface.
        
        Args:
            target_surface: Target pygame surface
            position: Position to render at (x, y)
        """
        try:
            target_surface.blit(self.surface, position)
        except Exception as e:
            print(f"❌ Surface rendering error: {e}")
    
    def get_camera_surface(self) -> pygame.Surface:
        """Get current camera view surface."""
        return self.surface
    
    def set_display_size(self, width: int, height: int):
        """
        Set display size.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        self.surface = pygame.Surface((self.width, self.height))
        print(f"✅ Display size set to: {width}x{height}")
    
    def set_fps(self, fps: int):
        """
        Set display frame rate.
        
        Args:
            fps: Frames per second
        """
        self.fps = max(1, min(60, fps))
        self.frame_delay = 1.0 / self.fps
        print(f"✅ Display FPS set to: {self.fps}")
    
    def set_annotation_style(self, style: str = "default"):
        """
        Set annotation visual style.
        
        Args:
            style: Style name ('default', 'minimal', 'colorful')
        """
        try:
            if style == "minimal":
                self.face_box_color = (200, 200, 200)
                self.unknown_face_color = (255, 100, 100)
                self.text_color = (255, 255, 255)
            elif style == "colorful":
                self.face_box_color = (0, 255, 100)
                self.unknown_face_color = (255, 100, 0)
                self.text_color = (255, 255, 100)
            else:  # default
                self.face_box_color = (0, 255, 0)
                self.unknown_face_color = (0, 0, 255)
                self.text_color = (255, 255, 255)
            
            print(f"✅ Annotation style set to: {style}")
            
        except Exception as e:
            print(f"❌ Style setting error: {e}")
    
    def test_display(self, duration: float = 3.0) -> bool:
        """
        Test camera view display with generated content.
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            True if test successful
        """
        try:
            print("🧪 Testing camera view display...")
            
            # Generate test frame
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            test_frame[:] = (50, 50, 100)  # Dark blue background
            
            # Add some test content
            cv2.putText(test_frame, "Test Camera View", (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Test face annotation
            test_annotation = {
                'face_location': (200, 150, 100, 100),
                'name': 'Test Person',
                'confidence': 0.95,
                'role': 'friend'
            }
            
            # Start display
            self.start_display(lambda: test_frame)
            self.update_frame(test_frame, [test_annotation])
            
            # Run test
            time.sleep(duration)
            
            # Stop display
            self.stop_display()
            
            print("✅ Camera view display test successful")
            return True
            
        except Exception as e:
            print(f"❌ Camera view display test error: {e}")
            return False
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information."""
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'is_displaying': self.is_displaying,
            'face_annotations_count': len(self.face_annotations),
            'has_current_frame': self.current_frame is not None
        }
    
    def cleanup(self):
        """Clean up display resources."""
        try:
            self.stop_display()
            print("🧹 Camera view display cleaned up")
        except Exception as e:
            print(f"❌ Camera view cleanup error: {e}")