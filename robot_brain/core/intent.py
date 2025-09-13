"""
🎯 Intent Recognition System

Analyzes speech input to determine user intent and route to appropriate handlers.
Supports both Bangla and English language processing.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    """Types of intents the robot can recognize."""
    GREETING = "greeting"
    QUESTION = "question"
    COMMAND = "command"
    ENTERTAINMENT = "entertainment"
    CAMERA_CAPTURE = "camera_capture"
    FACE_RECOGNITION = "face_recognition"
    MOVEMENT = "movement"
    SEARCH = "search"
    UNKNOWN = "unknown"

@dataclass
class Intent:
    """Represents a recognized intent with confidence and parameters."""
    type: IntentType
    confidence: float
    parameters: Dict[str, str]
    original_text: str
    language: str

class IntentRecognizer:
    """
    🧠 Intent Recognition Engine
    
    Uses pattern matching and keyword analysis to determine user intent.
    Supports both Bangla and English with cultural context awareness.
    """
    
    def __init__(self):
        """Initialize intent recognition patterns."""
        self.bangla_patterns = self._load_bangla_patterns()
        self.english_patterns = self._load_english_patterns()
        self.confidence_threshold = 0.6
    
    def _load_bangla_patterns(self) -> Dict[IntentType, List[str]]:
        """Load Bangla language patterns for intent recognition."""
        return {
            IntentType.GREETING: [
                r'আসসালামু আলাইকুম',
                r'নমস্কার',
                r'হ্যালো',
                r'কেমন আছেন',
                r'কেমন আছো',
                r'ভালো আছেন',
                r'ভালো আছো'
            ],
            IntentType.QUESTION: [
                r'কি\s+',
                r'কী\s+',
                r'কেন\s+',
                r'কখন\s+',
                r'কোথায়\s+',
                r'কিভাবে\s+',
                r'কাদের\s+',
                r'কাদেরকে\s+',
                r'জানতে চাই',
                r'বলুন',
                r'বলো',
                r'কি জানেন',
                r'কি জানো'
            ],
            IntentType.ENTERTAINMENT: [
                r'কৌতুক',
                r'জোক',
                r'গল্প',
                r'গান',
                r'মজার',
                r'হাসির',
                r'বিনোদন'
            ],
            IntentType.CAMERA_CAPTURE: [
                r'ছবি তুলো',
                r'ফটো নাও',
                r'চিত্র ধারণ',
                r'ক্যামেরা',
                r'আমার ছবি'
            ],
            IntentType.MOVEMENT: [
                r'এগিয়ে যাও',
                r'পিছনে যাও',
                r'ডানে যাও',
                r'বামে যাও',
                r'ঘুরো',
                r'হাত নাড়াও',
                r'মাথা নাড়াও'
            ],
            IntentType.SEARCH: [
                r'খুঁজে বের করো',
                r'ইন্টারনেটে দেখো',
                r'গুগলে দেখো',
                r'অনলাইনে দেখো'
            ]
        }
    
    def _load_english_patterns(self) -> Dict[IntentType, List[str]]:
        """Load English language patterns for intent recognition."""
        return {
            IntentType.GREETING: [
                r'hello',
                r'hi',
                r'hey',
                r'good morning',
                r'good afternoon',
                r'good evening',
                r'how are you',
                r'how do you do',
                r'nice to meet you'
            ],
            IntentType.QUESTION: [
                r'what\s+',
                r'why\s+',
                r'when\s+',
                r'where\s+',
                r'how\s+',
                r'who\s+',
                r'which\s+',
                r'can you tell me',
                r'do you know',
                r'explain',
                r'describe'
            ],
            IntentType.ENTERTAINMENT: [
                r'tell me a joke',
                r'joke',
                r'funny',
                r'story',
                r'sing',
                r'entertainment',
                r'play'
            ],
            IntentType.CAMERA_CAPTURE: [
                r'take a picture',
                r'take my photo',
                r'capture',
                r'camera',
                r'snapshot',
                r'photograph'
            ],
            IntentType.MOVEMENT: [
                r'move forward',
                r'move backward',
                r'turn left',
                r'turn right',
                r'wave hand',
                r'nod head',
                r'walk'
            ],
            IntentType.SEARCH: [
                r'search for',
                r'look up',
                r'find information',
                r'google',
                r'internet search'
            ]
        }
    
    def recognize(self, text: str, language: str) -> Intent:
        """
        Recognize intent from input text.
        
        Args:
            text: Input text to analyze
            language: Language code ('bn' or 'en')
            
        Returns:
            Intent object with type, confidence, and parameters
        """
        text = text.lower().strip()
        
        # Choose appropriate patterns based on language
        patterns = self.bangla_patterns if language == 'bn' else self.english_patterns
        
        best_intent = None
        best_confidence = 0.0
        
        # Check each intent type
        for intent_type, pattern_list in patterns.items():
            confidence = self._calculate_confidence(text, pattern_list)
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_type
        
        # Extract parameters if confidence is high enough
        parameters = {}
        if best_confidence >= self.confidence_threshold:
            parameters = self._extract_parameters(text, best_intent, language)
        
        return Intent(
            type=best_intent or IntentType.UNKNOWN,
            confidence=best_confidence,
            parameters=parameters,
            original_text=text,
            language=language
        )
    
    def _calculate_confidence(self, text: str, patterns: List[str]) -> float:
        """Calculate confidence score for a set of patterns."""
        max_confidence = 0.0
        
        for pattern in patterns:
            # Check for exact matches
            if re.search(pattern, text, re.IGNORECASE):
                confidence = 1.0
            else:
                # Check for partial matches
                words = text.split()
                pattern_words = pattern.replace(r'\s+', ' ').split()
                
                matches = 0
                for word in words:
                    for pattern_word in pattern_words:
                        if word in pattern_word or pattern_word in word:
                            matches += 1
                            break
                
                confidence = matches / len(pattern_words) if pattern_words else 0.0
            
            max_confidence = max(max_confidence, confidence)
        
        return max_confidence
    
    def _extract_parameters(self, text: str, intent_type: IntentType, language: str) -> Dict[str, str]:
        """Extract relevant parameters from the text based on intent type."""
        parameters = {}
        
        if intent_type == IntentType.QUESTION:
            # Extract the question topic
            if language == 'bn':
                # Remove common Bangla question words
                question_words = ['কি', 'কী', 'কেন', 'কখন', 'কোথায়', 'কিভাবে', 'কাদের', 'কাদেরকে']
                for word in question_words:
                    text = text.replace(word, '').strip()
            else:
                # Remove common English question words
                question_words = ['what', 'why', 'when', 'where', 'how', 'who', 'which']
                for word in question_words:
                    text = text.replace(word, '').strip()
            
            parameters['topic'] = text
        
        elif intent_type == IntentType.CAMERA_CAPTURE:
            # Check if it's a selfie request
            if language == 'bn':
                if any(word in text for word in ['আমার', 'আমাকে', 'সেলফি']):
                    parameters['target'] = 'self'
            else:
                if any(word in text for word in ['my', 'me', 'selfie']):
                    parameters['target'] = 'self'
        
        elif intent_type == IntentType.MOVEMENT:
            # Extract movement direction
            if language == 'bn':
                if 'এগিয়ে' in text or 'সামনে' in text:
                    parameters['direction'] = 'forward'
                elif 'পিছনে' in text:
                    parameters['direction'] = 'backward'
                elif 'ডানে' in text:
                    parameters['direction'] = 'right'
                elif 'বামে' in text:
                    parameters['direction'] = 'left'
            else:
                if 'forward' in text:
                    parameters['direction'] = 'forward'
                elif 'backward' in text or 'back' in text:
                    parameters['direction'] = 'backward'
                elif 'left' in text:
                    parameters['direction'] = 'left'
                elif 'right' in text:
                    parameters['direction'] = 'right'
        
        elif intent_type == IntentType.SEARCH:
            # Extract search query
            if language == 'bn':
                search_prefixes = ['খুঁজে বের করো', 'ইন্টারনেটে দেখো', 'গুগলে দেখো', 'অনলাইনে দেখো']
                for prefix in search_prefixes:
                    if prefix in text:
                        parameters['query'] = text.replace(prefix, '').strip()
                        break
            else:
                search_prefixes = ['search for', 'look up', 'find information about', 'google']
                for prefix in search_prefixes:
                    if prefix in text:
                        parameters['query'] = text.replace(prefix, '').strip()
                        break
        
        return parameters
    
    def get_intent_description(self, intent: Intent) -> str:
        """Get human-readable description of an intent."""
        descriptions = {
            IntentType.GREETING: "User is greeting the robot",
            IntentType.QUESTION: "User is asking a question",
            IntentType.COMMAND: "User is giving a command",
            IntentType.ENTERTAINMENT: "User wants entertainment",
            IntentType.CAMERA_CAPTURE: "User wants to take a photo",
            IntentType.FACE_RECOGNITION: "User wants face recognition",
            IntentType.MOVEMENT: "User wants robot to move",
            IntentType.SEARCH: "User wants to search the internet",
            IntentType.UNKNOWN: "Intent not recognized"
        }
        
        return descriptions.get(intent.type, "Unknown intent")