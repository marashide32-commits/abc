"""
🧠 Memory Management System

Handles long-term memory storage for face recognition, conversations,
and user preferences. Uses SQLite for persistent storage.
"""

import sqlite3
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Person:
    """Represents a person in the robot's memory."""
    id: int
    name: str
    face_encoding: str
    role: str
    language_preference: str
    first_met: str
    last_seen: str
    interaction_count: int
    notes: str

@dataclass
class Conversation:
    """Represents a conversation entry."""
    id: int
    timestamp: str
    user_name: str
    input_text: str
    input_language: str
    intent_type: str
    response_text: str
    response_language: str
    confidence: float

class MemoryManager:
    """
    🗄️ Memory Management System
    
    Handles persistent storage of:
    - Face recognition data
    - Conversation history
    - User preferences
    - System settings
    """
    
    def __init__(self, db_path: str = None):
        """Initialize memory manager with database connection."""
        from .config import config
        
        self.db_path = db_path or config.MEMORY_DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create people table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    face_encoding TEXT NOT NULL,
                    role TEXT DEFAULT 'friend',
                    language_preference TEXT DEFAULT 'bn',
                    first_met TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    interaction_count INTEGER DEFAULT 0,
                    notes TEXT DEFAULT ''
                )
            ''')
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_name TEXT,
                    input_text TEXT NOT NULL,
                    input_language TEXT NOT NULL,
                    intent_type TEXT NOT NULL,
                    response_text TEXT,
                    response_language TEXT,
                    confidence REAL DEFAULT 0.0
                )
            ''')
            
            # Create system settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
    
    def add_person(self, name: str, face_encoding: str, role: str = 'friend', 
                   language_preference: str = 'bn', notes: str = '') -> int:
        """
        Add a new person to memory.
        
        Args:
            name: Person's name
            face_encoding: Face encoding data (JSON string)
            role: Person's role (student, teacher, principal, etc.)
            language_preference: Preferred language ('bn' or 'en')
            notes: Additional notes about the person
            
        Returns:
            Person ID
        """
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO people (name, face_encoding, role, language_preference, 
                                  first_met, last_seen, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, face_encoding, role, language_preference, timestamp, timestamp, notes))
            
            person_id = cursor.lastrowid
            conn.commit()
            
            return person_id
    
    def get_person_by_name(self, name: str) -> Optional[Person]:
        """Get person information by name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, face_encoding, role, language_preference,
                       first_met, last_seen, interaction_count, notes
                FROM people WHERE name = ?
            ''', (name,))
            
            row = cursor.fetchone()
            if row:
                return Person(*row)
            return None
    
    def get_person_by_face_encoding(self, face_encoding: str, tolerance: float = 0.6) -> Optional[Person]:
        """
        Find person by face encoding with tolerance.
        
        Args:
            face_encoding: Face encoding to match
            tolerance: Matching tolerance (lower = stricter)
            
        Returns:
            Person object if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, face_encoding, role, language_preference,
                       first_met, last_seen, interaction_count, notes
                FROM people
            ''')
            
            for row in cursor.fetchall():
                person = Person(*row)
                stored_encoding = json.loads(person.face_encoding)
                input_encoding = json.loads(face_encoding)
                
                # Calculate face distance (simplified)
                if self._calculate_face_distance(stored_encoding, input_encoding) <= tolerance:
                    return person
            
            return None
    
    def update_person_last_seen(self, person_id: int):
        """Update last seen timestamp and interaction count for a person."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE people 
                SET last_seen = ?, interaction_count = interaction_count + 1
                WHERE id = ?
            ''', (datetime.now().isoformat(), person_id))
            
            conn.commit()
    
    def add_conversation(self, user_name: str, input_text: str, input_language: str,
                        intent_type: str, response_text: str = None, 
                        response_language: str = None, confidence: float = 0.0):
        """Add a conversation entry to memory."""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (timestamp, user_name, input_text, input_language,
                                        intent_type, response_text, response_language, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, user_name, input_text, input_language, intent_type,
                  response_text, response_language, confidence))
            
            conn.commit()
    
    def get_conversation_history(self, user_name: str = None, limit: int = 10) -> List[Conversation]:
        """Get recent conversation history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_name:
                cursor.execute('''
                    SELECT id, timestamp, user_name, input_text, input_language,
                           intent_type, response_text, response_language, confidence
                    FROM conversations 
                    WHERE user_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_name, limit))
            else:
                cursor.execute('''
                    SELECT id, timestamp, user_name, input_text, input_language,
                           intent_type, response_text, response_language, confidence
                    FROM conversations 
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            return [Conversation(*row) for row in rows]
    
    def get_user_preferences(self, user_name: str) -> Dict[str, Any]:
        """Get user preferences and context."""
        person = self.get_person_by_name(user_name)
        if not person:
            return {}
        
        # Get recent conversations for context
        recent_conversations = self.get_conversation_history(user_name, limit=5)
        
        return {
            'name': person.name,
            'role': person.role,
            'language_preference': person.language_preference,
            'interaction_count': person.interaction_count,
            'last_seen': person.last_seen,
            'recent_topics': [conv.intent_type for conv in recent_conversations],
            'notes': person.notes
        }
    
    def set_system_setting(self, key: str, value: str):
        """Set a system setting."""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, timestamp))
            
            conn.commit()
    
    def get_system_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a system setting."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM system_settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            return row[0] if row else default
    
    def _calculate_face_distance(self, encoding1: List[float], encoding2: List[float]) -> float:
        """
        Calculate distance between two face encodings.
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
            
        Returns:
            Distance value (lower = more similar)
        """
        if len(encoding1) != len(encoding2):
            return float('inf')
        
        # Calculate Euclidean distance
        distance = sum((a - b) ** 2 for a, b in zip(encoding1, encoding2)) ** 0.5
        return distance
    
    def get_all_people(self) -> List[Person]:
        """Get all people in memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, face_encoding, role, language_preference,
                       first_met, last_seen, interaction_count, notes
                FROM people
                ORDER BY last_seen DESC
            ''')
            
            rows = cursor.fetchall()
            return [Person(*row) for row in rows]
    
    def delete_person(self, person_id: int) -> bool:
        """Delete a person from memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM people WHERE id = ?', (person_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            
            return deleted
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count people
            cursor.execute('SELECT COUNT(*) FROM people')
            people_count = cursor.fetchone()[0]
            
            # Count conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            conversations_count = cursor.fetchone()[0]
            
            # Get most active users
            cursor.execute('''
                SELECT user_name, COUNT(*) as interaction_count
                FROM conversations 
                WHERE user_name IS NOT NULL
                GROUP BY user_name
                ORDER BY interaction_count DESC
                LIMIT 5
            ''')
            top_users = cursor.fetchall()
            
            return {
                'total_people': people_count,
                'total_conversations': conversations_count,
                'top_users': top_users,
                'database_size': Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            }