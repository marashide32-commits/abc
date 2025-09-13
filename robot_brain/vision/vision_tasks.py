"""
👁️ Vision Tasks Manager

High-level vision operations that coordinate camera and face recognition.
Handles complex vision tasks like taking selfies, face registration, and live monitoring.
"""

import cv2
import numpy as np
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

class VisionTasks:
    """
    🎯 Vision Tasks Manager
    
    Coordinates camera operations and face recognition for high-level vision tasks.
    Provides user-friendly interfaces for common vision operations.
    """
    
    def __init__(self, camera_manager, face_recognizer):
        """
        Initialize vision tasks manager.
        
        Args:
            camera_manager: CameraManager instance
            face_recognizer: FaceRecognizer instance
        """
        self.camera_manager = camera_manager
        self.face_recognizer = face_recognizer
        
        # Task settings
        self.face_detection_timeout = 10.0  # seconds
        self.photo_quality = 95  # JPEG quality (0-100)
        
        # Storage paths
        from ..core.config import config
        self.photos_dir = config.FACES_DIR.parent / "photos"
        self.photos_dir.mkdir(parents=True, exist_ok=True)
    
    def take_selfie(self, person_name: str = None) -> Optional[str]:
        """
        Take a selfie with face detection and recognition.
        
        Args:
            person_name: Name of person taking selfie (optional)
            
        Returns:
            Path to saved selfie or None if failed
        """
        try:
            print("📸 Taking selfie...")
            
            # Wait for face detection
            face_detected = False
            start_time = time.time()
            
            while not face_detected and (time.time() - start_time) < self.face_detection_timeout:
                frame = self.camera_manager.capture_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detect faces
                faces = self.face_recognizer.detect_faces(frame)
                
                if faces:
                    # Use the largest face
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, w, h = largest_face
                    
                    # Check if face is large enough (good quality)
                    if w > 100 and h > 100:
                        face_detected = True
                        
                        # Add a small delay for better photo
                        time.sleep(0.5)
                        final_frame = self.camera_manager.capture_frame()
                        
                        if final_frame is not None:
                            frame = final_frame
                        break
                
                time.sleep(0.1)
            
            if not face_detected:
                print("❌ No suitable face detected for selfie")
                return None
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if person_name:
                filename = f"selfie_{person_name}_{timestamp}.jpg"
            else:
                filename = f"selfie_{timestamp}.jpg"
            
            # Save selfie
            selfie_path = self.photos_dir / filename
            
            # Enhance image quality
            enhanced_frame = self._enhance_image(frame)
            
            success = cv2.imwrite(str(selfie_path), enhanced_frame, 
                                [cv2.IMWRITE_JPEG_QUALITY, self.photo_quality])
            
            if success:
                print(f"✅ Selfie saved: {selfie_path}")
                return str(selfie_path)
            else:
                print("❌ Failed to save selfie")
                return None
                
        except Exception as e:
            print(f"❌ Selfie capture error: {e}")
            return None
    
    def take_photo(self, description: str = None) -> Optional[str]:
        """
        Take a general photo.
        
        Args:
            description: Description of the photo
            
        Returns:
            Path to saved photo or None if failed
        """
        try:
            print("📷 Taking photo...")
            
            frame = self.camera_manager.capture_frame()
            
            if frame is None:
                print("❌ Could not capture frame")
                return None
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if description:
                safe_description = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"photo_{safe_description}_{timestamp}.jpg"
            else:
                filename = f"photo_{timestamp}.jpg"
            
            # Save photo
            photo_path = self.photos_dir / filename
            
            # Enhance image quality
            enhanced_frame = self._enhance_image(frame)
            
            success = cv2.imwrite(str(photo_path), enhanced_frame,
                                [cv2.IMWRITE_JPEG_QUALITY, self.photo_quality])
            
            if success:
                print(f"✅ Photo saved: {photo_path}")
                return str(photo_path)
            else:
                print("❌ Failed to save photo")
                return None
                
        except Exception as e:
            print(f"❌ Photo capture error: {e}")
            return None
    
    def register_new_face(self, name: str, role: str = 'friend', 
                         language_preference: str = 'bn', notes: str = '') -> bool:
        """
        Register a new face in the recognition system.
        
        Args:
            name: Person's name
            role: Person's role
            language_preference: Preferred language
            notes: Additional notes
            
        Returns:
            True if registration successful
        """
        try:
            print(f"👤 Registering new face: {name}")
            
            # Wait for face detection
            face_detected = False
            start_time = time.time()
            best_frame = None
            best_face = None
            
            while not face_detected and (time.time() - start_time) < self.face_detection_timeout:
                frame = self.camera_manager.capture_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detect faces
                faces = self.face_recognizer.detect_faces(frame)
                
                if faces:
                    # Find the best face (largest and most centered)
                    best_face = self._select_best_face(faces, frame.shape)
                    
                    if best_face:
                        x, y, w, h = best_face
                        
                        # Check if face is large enough and well-positioned
                        if w > 150 and h > 150:
                            face_detected = True
                            best_frame = frame
                            
                            # Add delay for better capture
                            time.sleep(0.5)
                            final_frame = self.camera_manager.capture_frame()
                            
                            if final_frame is not None:
                                best_frame = final_frame
                            break
                
                time.sleep(0.1)
            
            if not face_detected or best_frame is None:
                print("❌ No suitable face detected for registration")
                return False
            
            # Extract face region
            x, y, w, h = best_face
            face_image = best_frame[y:y+h, x:x+w]
            
            # Add face to recognition system
            success = self.face_recognizer.add_new_face(
                name=name,
                face_image=face_image,
                role=role,
                language_preference=language_preference,
                notes=notes
            )
            
            if success:
                # Save face photo for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                face_photo_path = self.photos_dir / f"registered_face_{name}_{timestamp}.jpg"
                cv2.imwrite(str(face_photo_path), face_image)
                
                print(f"✅ Face registered successfully: {name}")
                return True
            else:
                print(f"❌ Failed to register face: {name}")
                return False
                
        except Exception as e:
            print(f"❌ Face registration error: {e}")
            return False
    
    def monitor_faces(self, callback=None, duration: float = None) -> List[Dict[str, Any]]:
        """
        Monitor for faces and provide recognition results.
        
        Args:
            callback: Function to call with recognition results
            duration: Duration to monitor (None for continuous)
            
        Returns:
            List of recognition results
        """
        try:
            print("👁️ Starting face monitoring...")
            
            recognition_results = []
            start_time = time.time()
            last_recognition_time = 0
            recognition_cooldown = 2.0  # seconds between recognitions
            
            while True:
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                frame = self.camera_manager.capture_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Check cooldown
                current_time = time.time()
                if current_time - last_recognition_time < recognition_cooldown:
                    time.sleep(0.1)
                    continue
                
                # Detect and identify faces
                face_detected, person_info = self.face_recognizer.detect_and_identify(frame)
                
                if face_detected and person_info:
                    last_recognition_time = current_time
                    recognition_results.append(person_info)
                    
                    # Call callback if provided
                    if callback:
                        callback(person_info)
                
                time.sleep(0.1)
            
            print(f"✅ Face monitoring completed. Found {len(recognition_results)} recognitions")
            return recognition_results
            
        except Exception as e:
            print(f"❌ Face monitoring error: {e}")
            return []
    
    def get_live_feed_with_annotations(self, callback=None, duration: float = None):
        """
        Get live camera feed with face recognition annotations.
        
        Args:
            callback: Function to call with annotated frames
            duration: Duration to stream (None for continuous)
        """
        try:
            print("📹 Starting live feed with annotations...")
            
            start_time = time.time()
            
            while True:
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                frame = self.camera_manager.capture_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detect and identify faces
                face_detected, person_info = self.face_recognizer.detect_and_identify(frame)
                
                # Draw annotations
                if face_detected and person_info:
                    frame = self.face_recognizer.draw_face_annotations(frame, person_info)
                
                # Call callback with annotated frame
                if callback:
                    should_continue = callback(frame, person_info if face_detected else None)
                    if should_continue is False:
                        break
                
                time.sleep(1.0 / 30)  # 30 FPS max
                
        except Exception as e:
            print(f"❌ Live feed with annotations error: {e}")
    
    def _enhance_image(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better photos.
        
        Args:
            frame: Input frame
            
        Returns:
            Enhanced frame
        """
        try:
            # Convert to LAB color space for better enhancement
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            enhanced_lab = cv2.merge([l, a, b])
            enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            # Slight sharpening
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(enhanced_frame, -1, kernel)
            
            # Blend original and sharpened
            enhanced_frame = cv2.addWeighted(enhanced_frame, 0.7, sharpened, 0.3, 0)
            
            return enhanced_frame
            
        except Exception as e:
            print(f"❌ Image enhancement error: {e}")
            return frame
    
    def _select_best_face(self, faces: List[Tuple[int, int, int, int]], 
                         frame_shape: Tuple[int, int, int]) -> Optional[Tuple[int, int, int, int]]:
        """
        Select the best face from detected faces.
        
        Args:
            faces: List of face rectangles
            frame_shape: Frame dimensions
            
        Returns:
            Best face rectangle or None
        """
        if not faces:
            return None
        
        try:
            frame_height, frame_width = frame_shape[:2]
            center_x, center_y = frame_width // 2, frame_height // 2
            
            best_face = None
            best_score = 0
            
            for face in faces:
                x, y, w, h = face
                
                # Calculate face center
                face_center_x = x + w // 2
                face_center_y = y + h // 2
                
                # Calculate distance from frame center
                distance_from_center = np.sqrt(
                    (face_center_x - center_x) ** 2 + (face_center_y - center_y) ** 2
                )
                
                # Calculate face area
                face_area = w * h
                
                # Calculate score (larger faces closer to center are better)
                # Normalize distance (closer to 0 is better)
                normalized_distance = 1.0 - (distance_from_center / (frame_width // 2))
                normalized_area = face_area / (frame_width * frame_height)
                
                score = normalized_area * 0.7 + normalized_distance * 0.3
                
                if score > best_score:
                    best_score = score
                    best_face = face
            
            return best_face
            
        except Exception as e:
            print(f"❌ Face selection error: {e}")
            return faces[0] if faces else None
    
    def get_vision_stats(self) -> Dict[str, Any]:
        """Get vision system statistics."""
        return {
            'camera_initialized': self.camera_manager.is_initialized,
            'face_recognition_available': len(self.face_recognizer.known_faces) > 0,
            'known_faces_count': len(self.face_recognizer.known_faces),
            'photos_directory': str(self.photos_dir),
            'face_detection_timeout': self.face_detection_timeout,
            'photo_quality': self.photo_quality
        }