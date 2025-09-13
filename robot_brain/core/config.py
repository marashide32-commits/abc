"""
🔧 Configuration Management for Robot Brain

Centralized configuration for all robot brain modules.
Handles paths, settings, and environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    """Configuration class for robot brain settings."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    FACES_DIR: Path = DATA_DIR / "faces"
    LOGS_DIR: Path = DATA_DIR / "logs"
    MODELS_DIR: Path = DATA_DIR / "models"
    
    # Database
    MEMORY_DB_PATH: str = str(DATA_DIR / "memory.db")
    
    # Audio settings
    SAMPLE_RATE: int = 16000
    CHUNK_SIZE: int = 4000
    AUDIO_FORMAT: str = "int16"
    
    # Camera settings
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    CAMERA_FPS: int = 30
    
    # Face recognition
    FACE_ENCODING_TOLERANCE: float = 0.6
    FACE_DETECTION_SCALE: float = 0.25
    
    # AI Model settings
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "gemma:2b"
    MAX_RESPONSE_LENGTH: int = 500
    
    # Display settings
    DISPLAY_WIDTH: int = 800
    DISPLAY_HEIGHT: int = 480
    FONT_SIZE: int = 24
    
    # Speech recognition
    VOSK_MODEL_PATH: str = str(MODELS_DIR / "vosk-model-small-bn-0.22")
    LANGUAGE_DETECTION_CONFIDENCE: float = 0.8
    
    # TTS settings
    BANGLA_TTS_MODEL: str = "mobassir94/bangla-tts"
    ENGLISH_TTS_MODEL: str = "piper"
    
    # Internet search
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")
    SEARCH_ENGINE_ID: str = os.getenv("SEARCH_ENGINE_ID", "")
    
    def __post_init__(self):
        """Create necessary directories after initialization."""
        self.create_directories()
    
    def create_directories(self):
        """Create all necessary directories if they don't exist."""
        directories = [
            self.DATA_DIR,
            self.FACES_DIR,
            self.LOGS_DIR,
            self.MODELS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_model_path(self, model_name: str) -> str:
        """Get full path for a model file."""
        return str(self.MODELS_DIR / model_name)
    
    def get_face_path(self, person_name: str) -> str:
        """Get path for storing face images."""
        return str(self.FACES_DIR / f"{person_name}.jpg")
    
    def get_log_path(self, log_type: str) -> str:
        """Get path for log files."""
        return str(self.LOGS_DIR / f"{log_type}.log")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'project_root': str(self.PROJECT_ROOT),
            'data_dir': str(self.DATA_DIR),
            'faces_dir': str(self.FACES_DIR),
            'logs_dir': str(self.LOGS_DIR),
            'models_dir': str(self.MODELS_DIR),
            'memory_db_path': self.MEMORY_DB_PATH,
            'sample_rate': self.SAMPLE_RATE,
            'chunk_size': self.CHUNK_SIZE,
            'camera_width': self.CAMERA_WIDTH,
            'camera_height': self.CAMERA_HEIGHT,
            'camera_fps': self.CAMERA_FPS,
            'face_encoding_tolerance': self.FACE_ENCODING_TOLERANCE,
            'ollama_host': self.OLLAMA_HOST,
            'default_model': self.DEFAULT_MODEL,
            'display_width': self.DISPLAY_WIDTH,
            'display_height': self.DISPLAY_HEIGHT,
            'vosk_model_path': self.VOSK_MODEL_PATH,
            'bangla_tts_model': self.BANGLA_TTS_MODEL,
            'english_tts_model': self.ENGLISH_TTS_MODEL
        }

# Global configuration instance
config = Config()