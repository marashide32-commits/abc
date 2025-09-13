"""
🎮 Task Manager - Central Command Router

Routes intents to appropriate handlers and coordinates responses.
Acts as the central nervous system of the robot brain.
"""

import time
from typing import Dict, Any, Optional
from .intent import Intent, IntentType
from .memory import MemoryManager

class TaskManager:
    """
    🎯 Central Task Manager
    
    Routes user intents to appropriate handlers and coordinates responses.
    Manages the flow between different robot subsystems.
    """
    
    def __init__(self):
        """Initialize task manager with all handlers."""
        self.memory_manager = MemoryManager()
        self.handlers = self._initialize_handlers()
    
    def _initialize_handlers(self) -> Dict[IntentType, callable]:
        """Initialize intent handlers."""
        return {
            IntentType.GREETING: self._handle_greeting,
            IntentType.QUESTION: self._handle_question,
            IntentType.ENTERTAINMENT: self._handle_entertainment,
            IntentType.CAMERA_CAPTURE: self._handle_camera_capture,
            IntentType.MOVEMENT: self._handle_movement,
            IntentType.SEARCH: self._handle_search,
            IntentType.UNKNOWN: self._handle_unknown
        }
    
    def handle_intent(self, intent: Intent, text: str, language: str, current_user: str = None) -> str:
        """
        Handle an intent and return appropriate response.
        
        Args:
            intent: Recognized intent
            text: Original input text
            language: Input language
            current_user: Current user name (if known)
            
        Returns:
            Response text
        """
        try:
            # Log conversation to memory
            self.memory_manager.add_conversation(
                user_name=current_user,
                input_text=text,
                input_language=language,
                intent_type=intent.type.value,
                confidence=intent.confidence
            )
            
            # Get handler for intent type
            handler = self.handlers.get(intent.type, self._handle_unknown)
            
            # Execute handler
            response = handler(intent, current_user)
            
            # Log response to memory
            if response:
                self.memory_manager.add_conversation(
                    user_name=current_user,
                    input_text=text,
                    input_language=language,
                    intent_type=intent.type.value,
                    response_text=response,
                    response_language=language,
                    confidence=intent.confidence
                )
            
            return response
            
        except Exception as e:
            print(f"❌ Task manager error: {e}")
            return self._get_error_response(language)
    
    def _handle_greeting(self, intent: Intent, current_user: str = None) -> str:
        """Handle greeting intents."""
        if current_user:
            # Personalized greeting for known user
            user_info = self.memory_manager.get_user_preferences(current_user)
            role = user_info.get('role', 'friend')
            lang_pref = user_info.get('language_preference', 'bn')
            
            if lang_pref == 'bn':
                if role == 'principal':
                    return f"আসসালামু আলাইকুম, প্রিন্সিপাল স্যার! আপনার সাথে দেখা করে খুবই ভালো লাগছে।"
                elif role == 'teacher':
                    return f"আসসালামু আলাইকুম, স্যার! কেমন আছেন?"
                elif role == 'student':
                    return f"হ্যালো! কেমন আছো? আজকে ক্লাস কেমন গেছে?"
                else:
                    return f"আসসালামু আলাইকুম, {current_user}! কেমন আছেন?"
            else:
                if role == 'principal':
                    return f"Good day, Principal! It's wonderful to see you."
                elif role == 'teacher':
                    return f"Hello, Sir! How are you today?"
                elif role == 'student':
                    return f"Hi there! How was your class today?"
                else:
                    return f"Hello, {current_user}! Great to see you."
        else:
            # General greeting for unknown user
            if intent.language == 'bn':
                return "আসসালামু আলাইকুম! আমি আপনার রোবট সহকারী। আমি আপনার সাথে কথা বলতে প্রস্তুত।"
            else:
                return "Hello! I'm your robot assistant. I'm ready to help you."
    
    def _handle_question(self, intent: Intent, current_user: str = None) -> str:
        """Handle question intents."""
        topic = intent.parameters.get('topic', '')
        
        # Get user context for personalized responses
        user_context = ""
        if current_user:
            user_info = self.memory_manager.get_user_preferences(current_user)
            role = user_info.get('role', 'friend')
            user_context = f"User role: {role}. "
        
        # Route to AI system for answer
        from ..ai.response_router import ResponseRouter
        from ..ai.ollama_client import OllamaClient
        
        ollama_client = OllamaClient()
        response_router = ResponseRouter(ollama_client)
        
        # Prepare context-aware prompt
        prompt = f"{user_context}Question: {topic}"
        
        try:
            response = response_router.get_response(prompt, intent.language)
            return response
        except Exception as e:
            print(f"❌ AI response error: {e}")
            return self._get_fallback_response(intent.language)
    
    def _handle_entertainment(self, intent: Intent, current_user: str = None) -> str:
        """Handle entertainment requests."""
        from ..actions.entertainment import EntertainmentModule
        
        entertainment = EntertainmentModule()
        
        # Check user preferences for appropriate content
        if current_user:
            user_info = self.memory_manager.get_user_preferences(current_user)
            role = user_info.get('role', 'friend')
            
            # Different entertainment for different roles
            if role == 'principal':
                return entertainment.get_professional_content(intent.language)
            elif role == 'student':
                return entertainment.get_student_content(intent.language)
        
        # Default entertainment
        return entertainment.get_general_content(intent.language)
    
    def _handle_camera_capture(self, intent: Intent, current_user: str = None) -> str:
        """Handle camera capture requests."""
        from ..vision.vision_tasks import VisionTasks
        from ..vision.camera_utils import CameraManager
        from ..vision.face_recognition import FaceRecognizer
        
        try:
            camera_manager = CameraManager()
            face_recognizer = FaceRecognizer()
            vision_tasks = VisionTasks(camera_manager, face_recognizer)
            
            target = intent.parameters.get('target', 'general')
            
            if target == 'self':
                # Take selfie
                photo_path = vision_tasks.take_selfie()
                if photo_path:
                    if intent.language == 'bn':
                        return f"আপনার ছবি তোলা হয়েছে! ছবিটি {photo_path} এ সংরক্ষিত হয়েছে।"
                    else:
                        return f"Your photo has been taken! Saved to {photo_path}"
                else:
                    if intent.language == 'bn':
                        return "দুঃখিত, ছবি তোলা যায়নি। আবার চেষ্টা করুন।"
                    else:
                        return "Sorry, couldn't take the photo. Please try again."
            else:
                # Take general photo
                photo_path = vision_tasks.take_photo()
                if photo_path:
                    if intent.language == 'bn':
                        return f"ছবি তোলা হয়েছে! {photo_path} এ সংরক্ষিত হয়েছে।"
                    else:
                        return f"Photo taken! Saved to {photo_path}"
                else:
                    if intent.language == 'bn':
                        return "দুঃখিত, ছবি তোলা যায়নি।"
                    else:
                        return "Sorry, couldn't take the photo."
                        
        except Exception as e:
            print(f"❌ Camera error: {e}")
            return self._get_error_response(intent.language)
    
    def _handle_movement(self, intent: Intent, current_user: str = None) -> str:
        """Handle movement requests."""
        direction = intent.parameters.get('direction', '')
        
        # Check if movement is allowed for current user
        if current_user:
            user_info = self.memory_manager.get_user_preferences(current_user)
            role = user_info.get('role', 'friend')
            
            # Only allow movement for authorized users
            if role not in ['principal', 'teacher', 'admin']:
                if intent.language == 'bn':
                    return "দুঃখিত, আমি শুধুমাত্র শিক্ষক বা প্রিন্সিপালের নির্দেশে চলাফেরা করতে পারি।"
                else:
                    return "Sorry, I can only move when instructed by teachers or the principal."
        
        # Execute movement (placeholder - would interface with motor controllers)
        try:
            from ..actions.motion import MotionController
            motion = MotionController()
            
            if direction == 'forward':
                motion.move_forward()
            elif direction == 'backward':
                motion.move_backward()
            elif direction == 'left':
                motion.turn_left()
            elif direction == 'right':
                motion.turn_right()
            else:
                motion.wave_hand()
            
            if intent.language == 'bn':
                return f"ঠিক আছে, আমি {direction} দিকে যাচ্ছি।"
            else:
                return f"Okay, moving {direction}."
                
        except Exception as e:
            print(f"❌ Movement error: {e}")
            return self._get_error_response(intent.language)
    
    def _handle_search(self, intent: Intent, current_user: str = None) -> str:
        """Handle internet search requests."""
        query = intent.parameters.get('query', '')
        
        if not query:
            if intent.language == 'bn':
                return "কি খুঁজতে চান? অনুগ্রহ করে স্পষ্ট করে বলুন।"
            else:
                return "What would you like me to search for? Please be more specific."
        
        try:
            from ..ai.web_search import WebSearcher
            searcher = WebSearcher()
            
            results = searcher.search(query)
            
            if results:
                # Summarize results using AI
                from ..ai.response_router import ResponseRouter
                from ..ai.ollama_client import OllamaClient
                
                ollama_client = OllamaClient()
                response_router = ResponseRouter(ollama_client)
                
                summary_prompt = f"Summarize this search result in {intent.language}: {results[:500]}"
                summary = response_router.get_response(summary_prompt, intent.language)
                
                return summary
            else:
                if intent.language == 'bn':
                    return f"'{query}' সম্পর্কে কোনো তথ্য পাইনি। আবার চেষ্টা করুন।"
                else:
                    return f"Couldn't find information about '{query}'. Please try again."
                    
        except Exception as e:
            print(f"❌ Search error: {e}")
            return self._get_error_response(intent.language)
    
    def _handle_unknown(self, intent: Intent, current_user: str = None) -> str:
        """Handle unknown intents."""
        if intent.language == 'bn':
            return "দুঃখিত, আমি বুঝতে পারিনি। আপনি কি বলতে চেয়েছেন? আবার বলুন দয়া করে।"
        else:
            return "Sorry, I didn't understand. What would you like me to do? Please try again."
    
    def _get_error_response(self, language: str) -> str:
        """Get error response in appropriate language."""
        if language == 'bn':
            return "দুঃখিত, কিছু সমস্যা হয়েছে। আবার চেষ্টা করুন।"
        else:
            return "Sorry, something went wrong. Please try again."
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when AI is unavailable."""
        if language == 'bn':
            return "দুঃখিত, আমি এখন এই প্রশ্নের উত্তর দিতে পারছি না। পরে আবার চেষ্টা করুন।"
        else:
            return "Sorry, I can't answer that question right now. Please try again later."