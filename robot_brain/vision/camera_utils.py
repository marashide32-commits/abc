"""
📷 Camera Management System

Handles camera operations including capture, live feed, and image processing.
Compatible with Raspberry Pi Camera Module and USB cameras.
"""

import cv2
import numpy as np
import time
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

class CameraManager:
    """
    📸 Camera Management System
    
    Handles camera operations for the robot's vision system.
    Supports both Raspberry Pi Camera Module and USB cameras.
    """
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize camera manager.
        
        Args:
            camera_index: Camera device index (0 for default camera)
        """
        from ..core.config import config
        
        self.camera_index = camera_index
        self.camera = None
        self.is_initialized = False
        
        # Camera settings
        self.width = config.CAMERA_WIDTH
        self.height = config.CAMERA_HEIGHT
        self.fps = config.CAMERA_FPS
        
        # Image storage
        self.photos_dir = config.FACES_DIR.parent / "photos"
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        
        # Camera properties
        self.brightness = 50
        self.contrast = 50
        self.saturation = 50
        
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize camera connection."""
        try:
            print(f"📷 Initializing camera {self.camera_index}...")
            
            # Try to open camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Could not open camera {self.camera_index}")
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            self.camera.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.camera.set(cv2.CAP_PROP_SATURATION, self.saturation)
            
            # Verify settings
            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ Camera initialized: {actual_width}x{actual_height} @ {actual_fps:.1f}fps")
            self.is_initialized = True
            
        except Exception as e:
            print(f"❌ Camera initialization error: {e}")
            self.is_initialized = False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera.
        
        Returns:
            Captured frame or None if failed
        """
        if not self.is_initialized or not self.camera:
            print("❌ Camera not initialized")
            return None
        
        try:
            ret, frame = self.camera.read()
            
            if ret:
                return frame
            else:
                print("❌ Failed to capture frame")
                return None
                
        except Exception as e:
            print(f"❌ Frame capture error: {e}")
            return None
    
    def capture_photo(self, filename: str = None) -> Optional[str]:
        """
        Capture and save a photo.
        
        Args:
            filename: Custom filename (optional)
            
        Returns:
            Path to saved photo or None if failed
        """
        try:
            frame = self.capture_frame()
            
            if frame is None:
                return None
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}.jpg"
            
            # Ensure filename has extension
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filename += '.jpg'
            
            # Save photo
            photo_path = self.photos_dir / filename
            
            success = cv2.imwrite(str(photo_path), frame)
            
            if success:
                print(f"📸 Photo saved: {photo_path}")
                return str(photo_path)
            else:
                print("❌ Failed to save photo")
                return None
                
        except Exception as e:
            print(f"❌ Photo capture error: {e}")
            return None
    
    def get_live_feed(self, callback=None, duration: float = None):
        """
        Get live camera feed.
        
        Args:
            callback: Function to call with each frame
            duration: Duration to capture (None for continuous)
        """
        if not self.is_initialized or not self.camera:
            print("❌ Camera not initialized")
            return
        
        try:
            start_time = time.time()
            
            while True:
                frame = self.capture_frame()
                
                if frame is None:
                    break
                
                # Call callback if provided
                if callback:
                    should_continue = callback(frame)
                    if should_continue is False:
                        break
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Small delay to prevent overwhelming
                time.sleep(1.0 / self.fps)
                
        except Exception as e:
            print(f"❌ Live feed error: {e}")
    
    def detect_faces_in_frame(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a frame.
        
        Args:
            frame: Input frame
            
        Returns:
            List of face rectangles (x, y, w, h)
        """
        try:
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return faces.tolist()
            
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return []
    
    def draw_faces_on_frame(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Draw rectangles around detected faces.
        
        Args:
            frame: Input frame
            faces: List of face rectangles
            
        Returns:
            Frame with face rectangles drawn
        """
        try:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            return frame
            
        except Exception as e:
            print(f"❌ Face drawing error: {e}")
            return frame
    
    def capture_face_photo(self, person_name: str) -> Optional[str]:
        """
        Capture a photo specifically for face recognition.
        
        Args:
            person_name: Name of the person
            
        Returns:
            Path to saved face photo or None if failed
        """
        try:
            frame = self.capture_frame()
            
            if frame is None:
                return None
            
            # Detect faces
            faces = self.detect_faces_in_frame(frame)
            
            if not faces:
                print("❌ No faces detected in frame")
                return None
            
            # Use the largest face
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_image = frame[y:y+h, x:x+w]
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"face_{person_name}_{timestamp}.jpg"
            
            # Save face photo
            face_path = self.photos_dir / filename
            
            success = cv2.imwrite(str(face_path), face_image)
            
            if success:
                print(f"👤 Face photo saved: {face_path}")
                return str(face_path)
            else:
                print("❌ Failed to save face photo")
                return None
                
        except Exception as e:
            print(f"❌ Face photo capture error: {e}")
            return None
    
    def set_camera_property(self, property_name: str, value: float) -> bool:
        """
        Set camera property.
        
        Args:
            property_name: Property name (brightness, contrast, saturation)
            value: Property value (0-100)
            
        Returns:
            True if set successfully
        """
        if not self.is_initialized or not self.camera:
            return False
        
        try:
            property_map = {
                'brightness': cv2.CAP_PROP_BRIGHTNESS,
                'contrast': cv2.CAP_PROP_CONTRAST,
                'saturation': cv2.CAP_PROP_SATURATION,
                'hue': cv2.CAP_PROP_HUE,
                'gain': cv2.CAP_PROP_GAIN,
                'exposure': cv2.CAP_PROP_EXPOSURE
            }
            
            if property_name not in property_map:
                print(f"❌ Unknown camera property: {property_name}")
                return False
            
            # Set property
            success = self.camera.set(property_map[property_name], value)
            
            if success:
                # Update local value
                if property_name == 'brightness':
                    self.brightness = value
                elif property_name == 'contrast':
                    self.contrast = value
                elif property_name == 'saturation':
                    self.saturation = value
                
                print(f"✅ Camera {property_name} set to {value}")
                return True
            else:
                print(f"❌ Failed to set camera {property_name}")
                return False
                
        except Exception as e:
            print(f"❌ Camera property setting error: {e}")
            return False
    
    def get_camera_info(self) -> dict:
        """Get camera information and properties."""
        if not self.is_initialized or not self.camera:
            return {'initialized': False}
        
        try:
            return {
                'initialized': True,
                'camera_index': self.camera_index,
                'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.camera.get(cv2.CAP_PROP_FPS),
                'brightness': self.camera.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.camera.get(cv2.CAP_PROP_CONTRAST),
                'saturation': self.camera.get(cv2.CAP_PROP_SATURATION),
                'photos_dir': str(self.photos_dir)
            }
        except Exception as e:
            print(f"❌ Camera info error: {e}")
            return {'initialized': False, 'error': str(e)}
    
    def test_camera(self) -> bool:
        """Test camera functionality."""
        try:
            print("🧪 Testing camera...")
            
            # Test frame capture
            frame = self.capture_frame()
            
            if frame is None:
                print("❌ Camera test failed: Could not capture frame")
                return False
            
            # Test photo capture
            photo_path = self.capture_photo("test_photo.jpg")
            
            if photo_path and Path(photo_path).exists():
                print("✅ Camera test successful")
                # Clean up test photo
                try:
                    Path(photo_path).unlink()
                except:
                    pass
                return True
            else:
                print("❌ Camera test failed: Could not save photo")
                return False
                
        except Exception as e:
            print(f"❌ Camera test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up camera resources."""
        try:
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self.is_initialized = False
            print("🧹 Camera cleaned up")
            
        except Exception as e:
            print(f"❌ Camera cleanup error: {e}")