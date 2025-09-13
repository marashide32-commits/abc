"""
👁️ Face Recognition System

Advanced face detection and recognition using OpenCV and face_recognition library.
Handles face encoding, storage, and identification for personalized interactions.
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import face_recognition
from PIL import Image

class FaceRecognizer:
    """
    👤 Face Recognition Engine
    
    Handles face detection, encoding, and recognition using OpenCV and face_recognition.
    Provides personalized interactions based on recognized faces.
    """
    
    def __init__(self, tolerance: float = 0.6):
        """
        Initialize face recognition system.
        
        Args:
            tolerance: Face matching tolerance (lower = stricter matching)
        """
        from ..core.config import config
        
        self.tolerance = tolerance
        self.known_faces = {}
        self.known_encodings = []
        self.known_names = []
        
        # Camera settings
        self.camera_width = config.CAMERA_WIDTH
        self.camera_height = config.CAMERA_HEIGHT
        self.face_detection_scale = config.FACE_DETECTION_SCALE
        
        # Face detection settings
        self.face_cascade = None
        self._initialize_face_detection()
        
        # Load existing face data
        self._load_known_faces()
    
    def _initialize_face_detection(self):
        """Initialize OpenCV face detection cascade."""
        try:
            # Load Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise RuntimeError("Failed to load face cascade")
            
            print("✅ Face detection cascade loaded")
            
        except Exception as e:
            print(f"❌ Face detection initialization error: {e}")
            self.face_cascade = None
    
    def _load_known_faces(self):
        """Load known faces from memory database."""
        try:
            from ..core.memory import MemoryManager
            memory = MemoryManager()
            
            people = memory.get_all_people()
            
            for person in people:
                try:
                    # Parse face encoding
                    encoding = json.loads(person.face_encoding)
                    self.known_encodings.append(encoding)
                    self.known_names.append(person.name)
                    
                    self.known_faces[person.name] = {
                        'encoding': encoding,
                        'role': person.role,
                        'language_preference': person.language_preference,
                        'last_seen': person.last_seen,
                        'interaction_count': person.interaction_count
                    }
                    
                except Exception as e:
                    print(f"❌ Error loading face for {person.name}: {e}")
            
            print(f"✅ Loaded {len(self.known_faces)} known faces")
            
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List of face rectangles (x, y, w, h)
        """
        if self.face_cascade is None:
            return []
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Resize for faster detection
            small_frame = cv2.resize(gray, (0, 0), fx=self.face_detection_scale, fy=self.face_detection_scale)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                small_frame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Scale back to original size
            faces = [(int(x/self.face_detection_scale), int(y/self.face_detection_scale), 
                     int(w/self.face_detection_scale), int(h/self.face_detection_scale)) 
                    for (x, y, w, h) in faces]
            
            return faces
            
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return []
    
    def encode_face(self, face_image: np.ndarray) -> Optional[List[float]]:
        """
        Encode a face image to a face encoding.
        
        Args:
            face_image: Face image (BGR format)
            
        Returns:
            Face encoding as list of floats or None if failed
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Get face encodings
            encodings = face_recognition.face_encodings(rgb_image)
            
            if encodings:
                return encodings[0].tolist()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Face encoding error: {e}")
            return None
    
    def recognize_face(self, face_encoding: List[float]) -> Tuple[Optional[str], float]:
        """
        Recognize a face from its encoding.
        
        Args:
            face_encoding: Face encoding to match
            
        Returns:
            Tuple of (name, confidence) or (None, 0.0) if not recognized
        """
        if not self.known_encodings:
            return None, 0.0
        
        try:
            # Compare with known faces
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            # Find best match
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            
            # Check if match is within tolerance
            if best_distance <= self.tolerance:
                name = self.known_names[best_match_index]
                confidence = 1.0 - best_distance  # Convert distance to confidence
                return name, confidence
            else:
                return None, 0.0
                
        except Exception as e:
            print(f"❌ Face recognition error: {e}")
            return None, 0.0
    
    def detect_and_identify(self, frame: np.ndarray = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Detect and identify faces in a frame.
        
        Args:
            frame: Input frame (if None, will capture from camera)
            
        Returns:
            Tuple of (face_detected, person_info)
        """
        try:
            # If no frame provided, we'll need camera access
            if frame is None:
                # This would typically be called from camera manager
                return False, None
            
            # Detect faces
            faces = self.detect_faces(frame)
            
            if not faces:
                return False, None
            
            # Process the largest face
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_image = frame[y:y+h, x:x+w]
            
            # Encode face
            face_encoding = self.encode_face(face_image)
            
            if face_encoding is None:
                return True, None  # Face detected but couldn't encode
            
            # Recognize face
            name, confidence = self.recognize_face(face_encoding)
            
            if name:
                # Update last seen time
                from ..core.memory import MemoryManager
                memory = MemoryManager()
                person = memory.get_person_by_name(name)
                if person:
                    memory.update_person_last_seen(person.id)
                
                return True, {
                    'name': name,
                    'confidence': confidence,
                    'face_location': (x, y, w, h),
                    'face_encoding': face_encoding,
                    **self.known_faces[name]
                }
            else:
                return True, {
                    'name': 'Unknown',
                    'confidence': 0.0,
                    'face_location': (x, y, w, h),
                    'face_encoding': face_encoding
                }
                
        except Exception as e:
            print(f"❌ Face detection and identification error: {e}")
            return False, None
    
    def add_new_face(self, name: str, face_image: np.ndarray, 
                     role: str = 'friend', language_preference: str = 'bn',
                     notes: str = '') -> bool:
        """
        Add a new face to the recognition system.
        
        Args:
            name: Person's name
            face_image: Face image (BGR format)
            role: Person's role
            language_preference: Preferred language
            notes: Additional notes
            
        Returns:
            True if face added successfully
        """
        try:
            # Encode face
            face_encoding = self.encode_face(face_image)
            
            if face_encoding is None:
                print("❌ Could not encode face")
                return False
            
            # Add to known faces
            self.known_encodings.append(face_encoding)
            self.known_names.append(name)
            
            self.known_faces[name] = {
                'encoding': face_encoding,
                'role': role,
                'language_preference': language_preference,
                'last_seen': time.strftime('%Y-%m-%d %H:%M:%S'),
                'interaction_count': 0
            }
            
            # Save to memory database
            from ..core.memory import MemoryManager
            memory = MemoryManager()
            
            memory.add_person(
                name=name,
                face_encoding=json.dumps(face_encoding),
                role=role,
                language_preference=language_preference,
                notes=notes
            )
            
            print(f"✅ Added new face: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding face: {e}")
            return False
    
    def get_face_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a known face."""
        return self.known_faces.get(name)
    
    def get_all_known_faces(self) -> Dict[str, Dict[str, Any]]:
        """Get all known faces information."""
        return self.known_faces.copy()
    
    def remove_face(self, name: str) -> bool:
        """
        Remove a face from the recognition system.
        
        Args:
            name: Name of person to remove
            
        Returns:
            True if removed successfully
        """
        try:
            if name not in self.known_faces:
                return False
            
            # Remove from local data
            del self.known_faces[name]
            
            # Remove from encoding lists
            if name in self.known_names:
                index = self.known_names.index(name)
                self.known_names.pop(index)
                self.known_encodings.pop(index)
            
            # Remove from memory database
            from ..core.memory import MemoryManager
            memory = MemoryManager()
            person = memory.get_person_by_name(name)
            if person:
                memory.delete_person(person.id)
            
            print(f"✅ Removed face: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error removing face: {e}")
            return False
    
    def update_face_info(self, name: str, **kwargs) -> bool:
        """
        Update information for a known face.
        
        Args:
            name: Name of person
            **kwargs: Fields to update (role, language_preference, notes)
            
        Returns:
            True if updated successfully
        """
        try:
            if name not in self.known_faces:
                return False
            
            # Update local data
            for key, value in kwargs.items():
                if key in self.known_faces[name]:
                    self.known_faces[name][key] = value
            
            # Update memory database
            from ..core.memory import MemoryManager
            memory = MemoryManager()
            person = memory.get_person_by_name(name)
            
            if person:
                # Update person in database
                # This would require extending the memory manager
                pass
            
            print(f"✅ Updated face info for: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating face info: {e}")
            return False
    
    def draw_face_annotations(self, frame: np.ndarray, person_info: Dict[str, Any]) -> np.ndarray:
        """
        Draw face annotations on frame.
        
        Args:
            frame: Input frame
            person_info: Person information from recognition
            
        Returns:
            Frame with annotations
        """
        try:
            if 'face_location' not in person_info:
                return frame
            
            x, y, w, h = person_info['face_location']
            name = person_info.get('name', 'Unknown')
            confidence = person_info.get('confidence', 0.0)
            role = person_info.get('role', 'friend')
            
            # Draw face rectangle
            color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{name} ({role})"
            if confidence > 0:
                label += f" {confidence:.1%}"
            
            # Label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                         (x + label_size[0], y), color, -1)
            
            # Label text
            cv2.putText(frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            return frame
            
        except Exception as e:
            print(f"❌ Error drawing face annotations: {e}")
            return frame
    
    def get_recognition_stats(self) -> Dict[str, Any]:
        """Get face recognition statistics."""
        return {
            'total_known_faces': len(self.known_faces),
            'tolerance': self.tolerance,
            'face_detection_scale': self.face_detection_scale,
            'known_names': list(self.known_faces.keys()),
            'cascade_loaded': self.face_cascade is not None
        }
    
    def test_face_recognition(self, test_image_path: str) -> bool:
        """
        Test face recognition with a sample image.
        
        Args:
            test_image_path: Path to test image
            
        Returns:
            True if test successful
        """
        try:
            if not Path(test_image_path).exists():
                print(f"❌ Test image not found: {test_image_path}")
                return False
            
            # Load test image
            frame = cv2.imread(test_image_path)
            if frame is None:
                print("❌ Could not load test image")
                return False
            
            # Test face detection
            faces = self.detect_faces(frame)
            print(f"🧪 Detected {len(faces)} faces in test image")
            
            if faces:
                # Test face recognition
                face_detected, person_info = self.detect_and_identify(frame)
                if face_detected:
                    print(f"✅ Face recognition test successful: {person_info}")
                    return True
            
            print("❌ Face recognition test failed")
            return False
            
        except Exception as e:
            print(f"❌ Face recognition test error: {e}")
            return False