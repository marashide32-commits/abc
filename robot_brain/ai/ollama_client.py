"""
🤖 Ollama AI Client

Interface to Ollama API for running local AI models.
Supports gemma:2b and other models for natural language processing.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

class OllamaClient:
    """
    🧠 Ollama AI Client
    
    Interface to Ollama API for running local AI models.
    Provides conversation capabilities with context awareness.
    """
    
    def __init__(self, host: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama server host URL
        """
        from ..core.config import config
        
        self.host = host or config.OLLAMA_HOST
        self.default_model = config.DEFAULT_MODEL
        self.max_response_length = config.MAX_RESPONSE_LENGTH
        
        # Connection settings
        self.timeout = 30
        self.retry_attempts = 3
        self.retry_delay = 1
        
        # Model settings
        self.model_options = {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 500,
            'stop': ['Human:', 'User:', 'Assistant:']
        }
        
        # Test connection
        self.is_available = self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server connection successful")
                return True
            else:
                print(f"❌ Ollama server error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ollama server connection failed: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models.
        
        Returns:
            List of model information
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            else:
                print(f"❌ Failed to get models: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return []
    
    def pull_model(self, model_name: str, callback: Callable = None) -> bool:
        """
        Pull/download a model from Ollama registry.
        
        Args:
            model_name: Name of model to pull
            callback: Progress callback function
            
        Returns:
            True if successful
        """
        try:
            print(f"📥 Pulling model: {model_name}")
            
            payload = {'name': model_name}
            
            response = requests.post(
                f"{self.host}/api/pull",
                json=payload,
                stream=True,
                timeout=300  # 5 minutes for model download
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            
                            if callback:
                                callback(data)
                            
                            if data.get('status') == 'success':
                                print(f"✅ Model {model_name} pulled successfully")
                                return True
                                
                        except json.JSONDecodeError:
                            continue
                
                return True
            else:
                print(f"❌ Failed to pull model: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error pulling model: {e}")
            return False
    
    def generate_response(self, prompt: str, model: str = None, 
                         context: List[str] = None, 
                         options: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate response from AI model.
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            context: Conversation context
            options: Model options
            
        Returns:
            Generated response or None if failed
        """
        if not self.is_available:
            print("❌ Ollama server not available")
            return None
        
        model = model or self.default_model
        
        try:
            # Prepare request payload
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {**self.model_options, **(options or {})}
            }
            
            # Add context if provided
            if context:
                payload['context'] = context
            
            # Make request with retries
            for attempt in range(self.retry_attempts):
                try:
                    response = requests.post(
                        f"{self.host}/api/generate",
                        json=payload,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        response_text = data.get('response', '').strip()
                        
                        # Limit response length
                        if len(response_text) > self.max_response_length:
                            response_text = response_text[:self.max_response_length] + "..."
                        
                        return response_text
                    else:
                        print(f"❌ Generation failed: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"⏰ Request timeout (attempt {attempt + 1})")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(self.retry_delay)
                        continue
                
                except Exception as e:
                    print(f"❌ Generation error (attempt {attempt + 1}): {e}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(self.retry_delay)
                        continue
            
            return None
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return None
    
    def generate_streaming(self, prompt: str, model: str = None,
                          callback: Callable = None,
                          options: Dict[str, Any] = None):
        """
        Generate streaming response from AI model.
        
        Args:
            prompt: Input prompt
            model: Model name
            callback: Function to call with each chunk
            options: Model options
        """
        if not self.is_available:
            print("❌ Ollama server not available")
            return
        
        model = model or self.default_model
        
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': True,
                'options': {**self.model_options, **(options or {})}
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            
                            if callback:
                                callback(data)
                            
                            if data.get('done', False):
                                break
                                
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"❌ Streaming failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Streaming error: {e}")
    
    def chat(self, messages: List[Dict[str, str]], model: str = None,
             options: Dict[str, Any] = None) -> Optional[str]:
        """
        Chat with AI model using message history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name
            options: Model options
            
        Returns:
            AI response or None if failed
        """
        if not self.is_available:
            print("❌ Ollama server not available")
            return None
        
        model = model or self.default_model
        
        try:
            payload = {
                'model': model,
                'messages': messages,
                'stream': False,
                'options': {**self.model_options, **(options or {})}
            }
            
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})
                response_text = message.get('content', '').strip()
                
                # Limit response length
                if len(response_text) > self.max_response_length:
                    response_text = response_text[:self.max_response_length] + "..."
                
                return response_text
            else:
                print(f"❌ Chat failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return None
    
    def get_model_info(self, model: str = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a model.
        
        Args:
            model: Model name (uses default if None)
            
        Returns:
            Model information or None if failed
        """
        if not self.is_available:
            return None
        
        model = model or self.default_model
        
        try:
            payload = {'name': model}
            
            response = requests.post(
                f"{self.host}/api/show",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get model info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting model info: {e}")
            return None
    
    def set_model_options(self, **options):
        """
        Set default model options.
        
        Args:
            **options: Model options to set
        """
        self.model_options.update(options)
        print(f"✅ Model options updated: {options}")
    
    def test_model(self, model: str = None, test_prompt: str = "Hello, how are you?") -> bool:
        """
        Test a model with a simple prompt.
        
        Args:
            model: Model name to test
            test_prompt: Test prompt
            
        Returns:
            True if test successful
        """
        try:
            print(f"🧪 Testing model: {model or self.default_model}")
            
            response = self.generate_response(test_prompt, model)
            
            if response:
                print(f"✅ Model test successful: {response[:100]}...")
                return True
            else:
                print("❌ Model test failed")
                return False
                
        except Exception as e:
            print(f"❌ Model test error: {e}")
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information and status."""
        return {
            'host': self.host,
            'default_model': self.default_model,
            'is_available': self.is_available,
            'timeout': self.timeout,
            'retry_attempts': self.retry_attempts,
            'model_options': self.model_options,
            'max_response_length': self.max_response_length
        }