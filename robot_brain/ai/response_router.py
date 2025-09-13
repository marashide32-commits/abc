"""
🎯 AI Response Router

Routes requests to appropriate AI models based on language and context.
Manages conversation flow and provides intelligent responses.
"""

import time
from typing import Dict, List, Optional, Any
from .ollama_client import OllamaClient

class ResponseRouter:
    """
    🧭 AI Response Router
    
    Routes requests to appropriate AI models and manages conversation context.
    Provides intelligent responses based on language, user role, and context.
    """
    
    def __init__(self, ollama_client: OllamaClient):
        """
        Initialize response router.
        
        Args:
            ollama_client: OllamaClient instance
        """
        self.ollama_client = ollama_client
        
        # Model assignments
        self.bangla_model = "gemma:2b"  # Primary model for Bangla
        self.english_model = "gemma:2b"  # Primary model for English
        self.fallback_model = "gemma:2b"  # Fallback model
        
        # Conversation context
        self.conversation_history = []
        self.max_history_length = 10
        
        # Response templates and prompts
        self.system_prompts = self._initialize_system_prompts()
    
    def _initialize_system_prompts(self) -> Dict[str, str]:
        """Initialize system prompts for different contexts."""
        return {
            'bangla_general': """আপনি একটি বন্ধুত্বপূর্ণ রোবট সহকারী। আপনি বাংলা ভাষায় কথা বলুন এবং সহায়তা প্রদান করুন। 
            আপনার উত্তর সংক্ষিপ্ত, স্পষ্ট এবং বন্ধুত্বপূর্ণ হওয়া উচিত।""",
            
            'bangla_school': """আপনি একটি স্কুলের রোবট সহকারী। আপনি শিক্ষক, ছাত্র এবং প্রিন্সিপালের সাথে কথা বলুন।
            আপনি শিক্ষামূলক বিষয়ে সাহায্য করতে পারেন এবং স্কুলের নিয়ম-কানুন সম্পর্কে জানাতে পারেন।""",
            
            'english_general': """You are a friendly robot assistant. Provide helpful, concise, and clear responses.
            Be polite and professional in your interactions.""",
            
            'english_school': """You are a school robot assistant. Help teachers, students, and the principal.
            You can assist with educational topics and provide information about school policies."""
        }
    
    def get_response(self, user_input: str, language: str = 'en', 
                    user_context: Dict[str, Any] = None) -> Optional[str]:
        """
        Get AI response for user input.
        
        Args:
            user_input: User's input text
            language: Language code ('bn' or 'en')
            user_context: User context information
            
        Returns:
            AI response or None if failed
        """
        try:
            # Determine appropriate model and prompt
            model, system_prompt = self._select_model_and_prompt(language, user_context)
            
            # Prepare conversation context
            messages = self._prepare_conversation_context(user_input, system_prompt, language)
            
            # Get response from AI
            response = self.ollama_client.chat(messages, model)
            
            if response:
                # Add to conversation history
                self._add_to_history(user_input, response, language)
                
                # Post-process response
                processed_response = self._post_process_response(response, language)
                
                return processed_response
            else:
                return self._get_fallback_response(language)
                
        except Exception as e:
            print(f"❌ Response routing error: {e}")
            return self._get_fallback_response(language)
    
    def _select_model_and_prompt(self, language: str, user_context: Dict[str, Any] = None) -> tuple:
        """
        Select appropriate model and system prompt.
        
        Args:
            language: Language code
            user_context: User context
            
        Returns:
            Tuple of (model_name, system_prompt)
        """
        # Select model based on language
        if language == 'bn':
            model = self.bangla_model
        else:
            model = self.english_model
        
        # Select system prompt based on context
        if user_context:
            role = user_context.get('role', 'friend')
            if role in ['teacher', 'principal', 'student']:
                prompt_key = f"{language}_school"
            else:
                prompt_key = f"{language}_general"
        else:
            prompt_key = f"{language}_general"
        
        system_prompt = self.system_prompts.get(prompt_key, self.system_prompts[f"{language}_general"])
        
        return model, system_prompt
    
    def _prepare_conversation_context(self, user_input: str, system_prompt: str, 
                                    language: str) -> List[Dict[str, str]]:
        """
        Prepare conversation context for AI.
        
        Args:
            user_input: Current user input
            system_prompt: System prompt
            language: Language code
            
        Returns:
            List of message dictionaries
        """
        messages = [
            {'role': 'system', 'content': system_prompt}
        ]
        
        # Add recent conversation history
        for entry in self.conversation_history[-5:]:  # Last 5 exchanges
            if entry['language'] == language:
                messages.append({'role': 'user', 'content': entry['user_input']})
                messages.append({'role': 'assistant', 'content': entry['response']})
        
        # Add current user input
        messages.append({'role': 'user', 'content': user_input})
        
        return messages
    
    def _add_to_history(self, user_input: str, response: str, language: str):
        """Add conversation to history."""
        self.conversation_history.append({
            'timestamp': time.time(),
            'user_input': user_input,
            'response': response,
            'language': language
        })
        
        # Limit history length
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def _post_process_response(self, response: str, language: str) -> str:
        """
        Post-process AI response.
        
        Args:
            response: Raw AI response
            language: Language code
            
        Returns:
            Processed response
        """
        # Clean up response
        response = response.strip()
        
        # Remove common AI prefixes
        prefixes_to_remove = [
            "Assistant:", "Robot:", "AI:", "রোবট:", "সহকারী:",
            "I am", "আমি", "As an AI", "As a robot"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
                break
        
        # Ensure proper sentence ending
        if language == 'bn':
            if not response.endswith(('.', '!', '?', '।')):
                response += '।'
        else:
            if not response.endswith(('.', '!', '?')):
                response += '.'
        
        return response
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when AI is unavailable."""
        fallback_responses = {
            'bn': "দুঃখিত, আমি এখন উত্তর দিতে পারছি না। পরে আবার চেষ্টা করুন।",
            'en': "Sorry, I can't provide a response right now. Please try again later."
        }
        
        return fallback_responses.get(language, fallback_responses['en'])
    
    def get_educational_response(self, topic: str, language: str = 'en', 
                               grade_level: str = None) -> Optional[str]:
        """
        Get educational response for a specific topic.
        
        Args:
            topic: Educational topic
            language: Language code
            grade_level: Grade level (e.g., 'primary', 'secondary')
            
        Returns:
            Educational response or None if failed
        """
        try:
            # Create educational prompt
            if language == 'bn':
                prompt = f"শিক্ষামূলক বিষয়: {topic}"
                if grade_level:
                    prompt += f" (শ্রেণী: {grade_level})"
                prompt += "। দয়া করে সহজ এবং বোধগম্য ভাষায় ব্যাখ্যা করুন।"
            else:
                prompt = f"Educational topic: {topic}"
                if grade_level:
                    prompt += f" (Grade level: {grade_level})"
                prompt += ". Please explain in simple and understandable language."
            
            return self.get_response(prompt, language)
            
        except Exception as e:
            print(f"❌ Educational response error: {e}")
            return None
    
    def get_entertainment_response(self, request_type: str, language: str = 'en') -> Optional[str]:
        """
        Get entertainment response (jokes, stories, etc.).
        
        Args:
            request_type: Type of entertainment ('joke', 'story', 'riddle')
            language: Language code
            
        Returns:
            Entertainment response or None if failed
        """
        try:
            if language == 'bn':
                if request_type == 'joke':
                    prompt = "একটি মজার কৌতুক বলুন।"
                elif request_type == 'story':
                    prompt = "একটি ছোট গল্প বলুন।"
                elif request_type == 'riddle':
                    prompt = "একটি ধাঁধা বলুন।"
                else:
                    prompt = "কিছু মজার বলুন।"
            else:
                if request_type == 'joke':
                    prompt = "Tell me a funny joke."
                elif request_type == 'story':
                    prompt = "Tell me a short story."
                elif request_type == 'riddle':
                    prompt = "Tell me a riddle."
                else:
                    prompt = "Tell me something entertaining."
            
            return self.get_response(prompt, language)
            
        except Exception as e:
            print(f"❌ Entertainment response error: {e}")
            return None
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        print("🗑️ Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation history."""
        return {
            'total_exchanges': len(self.conversation_history),
            'languages_used': list(set(entry['language'] for entry in self.conversation_history)),
            'last_interaction': self.conversation_history[-1]['timestamp'] if self.conversation_history else None,
            'recent_topics': [entry['user_input'][:50] + '...' for entry in self.conversation_history[-3:]]
        }
    
    def set_model_preferences(self, bangla_model: str = None, english_model: str = None):
        """
        Set model preferences for different languages.
        
        Args:
            bangla_model: Model for Bangla responses
            english_model: Model for English responses
        """
        if bangla_model:
            self.bangla_model = bangla_model
            print(f"✅ Bangla model set to: {bangla_model}")
        
        if english_model:
            self.english_model = english_model
            print(f"✅ English model set to: {english_model}")
    
    def test_response_system(self, test_input: str = "Hello, how are you?", 
                           language: str = 'en') -> bool:
        """
        Test the response system.
        
        Args:
            test_input: Test input
            language: Language code
            
        Returns:
            True if test successful
        """
        try:
            print(f"🧪 Testing response system ({language})...")
            
            response = self.get_response(test_input, language)
            
            if response:
                print(f"✅ Response system test successful: {response[:100]}...")
                return True
            else:
                print("❌ Response system test failed")
                return False
                
        except Exception as e:
            print(f"❌ Response system test error: {e}")
            return False