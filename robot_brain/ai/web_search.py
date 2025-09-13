"""
🌐 Web Search Integration

Provides internet search capabilities when the robot cannot answer questions locally.
Uses Google Custom Search API for reliable search results.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus

class WebSearcher:
    """
    🔍 Web Search Engine
    
    Provides internet search capabilities for the robot when local AI cannot answer.
    Uses Google Custom Search API for reliable and relevant results.
    """
    
    def __init__(self, api_key: str = None, search_engine_id: str = None):
        """
        Initialize web searcher.
        
        Args:
            api_key: Google Custom Search API key
            search_engine_id: Custom Search Engine ID
        """
        from ..core.config import config
        
        self.api_key = api_key or config.SEARCH_API_KEY
        self.search_engine_id = search_engine_id or config.SEARCH_ENGINE_ID
        
        # Search settings
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.max_results = 5
        self.timeout = 10
        
        # Check if API credentials are available
        self.is_available = bool(self.api_key and self.search_engine_id)
        
        if not self.is_available:
            print("⚠️ Web search not available: Missing API credentials")
        else:
            print("✅ Web search initialized")
    
    def search(self, query: str, language: str = 'en', num_results: int = None) -> Optional[str]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            language: Language code ('bn' or 'en')
            num_results: Number of results to return
            
        Returns:
            Formatted search results or None if failed
        """
        if not self.is_available:
            print("❌ Web search not available")
            return None
        
        try:
            print(f"🔍 Searching for: {query}")
            
            # Prepare search parameters
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results or self.max_results,
                'safe': 'medium'
            }
            
            # Add language preference
            if language == 'bn':
                params['lr'] = 'lang_bn'
            else:
                params['lr'] = 'lang_en'
            
            # Make search request
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_search_results(data, language)
            else:
                print(f"❌ Search failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return None
    
    def _format_search_results(self, data: Dict[str, Any], language: str) -> str:
        """
        Format search results into readable text.
        
        Args:
            data: Search API response data
            language: Language code
            
        Returns:
            Formatted search results
        """
        try:
            items = data.get('items', [])
            
            if not items:
                if language == 'bn':
                    return "দুঃখিত, এই বিষয়ে কোনো তথ্য পাইনি।"
                else:
                    return "Sorry, no information found on this topic."
            
            # Format results
            if language == 'bn':
                result_text = "খুঁজে পাওয়া তথ্য:\n\n"
            else:
                result_text = "Search results:\n\n"
            
            for i, item in enumerate(items[:3], 1):  # Limit to top 3 results
                title = item.get('title', 'No title')
                snippet = item.get('snippet', 'No description')
                url = item.get('link', '')
                
                # Clean up snippet
                snippet = snippet.replace('\n', ' ').strip()
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."
                
                result_text += f"{i}. {title}\n"
                result_text += f"   {snippet}\n"
                if url:
                    result_text += f"   সূত্র: {url}\n" if language == 'bn' else f"   Source: {url}\n"
                result_text += "\n"
            
            return result_text.strip()
            
        except Exception as e:
            print(f"❌ Error formatting results: {e}")
            return "Error processing search results."
    
    def search_news(self, topic: str, language: str = 'en') -> Optional[str]:
        """
        Search for recent news on a topic.
        
        Args:
            topic: News topic
            language: Language code
            
        Returns:
            Formatted news results or None if failed
        """
        try:
            # Add news-specific terms to query
            if language == 'bn':
                news_query = f"{topic} খবর"
            else:
                news_query = f"{topic} news"
            
            return self.search(news_query, language, num_results=3)
            
        except Exception as e:
            print(f"❌ News search error: {e}")
            return None
    
    def search_educational(self, topic: str, language: str = 'en') -> Optional[str]:
        """
        Search for educational content on a topic.
        
        Args:
            topic: Educational topic
            language: Language code
            
        Returns:
            Formatted educational results or None if failed
        """
        try:
            # Add educational terms to query
            if language == 'bn':
                edu_query = f"{topic} শিক্ষা ব্যাখ্যা"
            else:
                edu_query = f"{topic} education explanation"
            
            return self.search(edu_query, language, num_results=3)
            
        except Exception as e:
            print(f"❌ Educational search error: {e}")
            return None
    
    def search_weather(self, location: str, language: str = 'en') -> Optional[str]:
        """
        Search for weather information.
        
        Args:
            location: Location name
            language: Language code
            
        Returns:
            Weather information or None if failed
        """
        try:
            if language == 'bn':
                weather_query = f"{location} আবহাওয়া"
            else:
                weather_query = f"{location} weather"
            
            return self.search(weather_query, language, num_results=2)
            
        except Exception as e:
            print(f"❌ Weather search error: {e}")
            return None
    
    def search_definition(self, word: str, language: str = 'en') -> Optional[str]:
        """
        Search for word definition.
        
        Args:
            word: Word to define
            language: Language code
            
        Returns:
            Word definition or None if failed
        """
        try:
            if language == 'bn':
                def_query = f"{word} অর্থ"
            else:
                def_query = f"{word} definition meaning"
            
            return self.search(def_query, language, num_results=2)
            
        except Exception as e:
            print(f"❌ Definition search error: {e}")
            return None
    
    def get_search_suggestions(self, partial_query: str, language: str = 'en') -> List[str]:
        """
        Get search suggestions for a partial query.
        
        Args:
            partial_query: Partial search query
            language: Language code
            
        Returns:
            List of search suggestions
        """
        try:
            # This would typically use Google's autocomplete API
            # For now, return some basic suggestions
            suggestions = []
            
            if language == 'bn':
                common_queries = [
                    "কিভাবে", "কি", "কেন", "কখন", "কোথায়",
                    "শিক্ষা", "খবর", "আবহাওয়া", "স্বাস্থ্য"
                ]
            else:
                common_queries = [
                    "how to", "what is", "why", "when", "where",
                    "education", "news", "weather", "health"
                ]
            
            for query in common_queries:
                if partial_query.lower() in query.lower():
                    suggestions.append(f"{partial_query} {query}")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            print(f"❌ Search suggestions error: {e}")
            return []
    
    def test_search(self, test_query: str = "artificial intelligence") -> bool:
        """
        Test the search functionality.
        
        Args:
            test_query: Test search query
            
        Returns:
            True if test successful
        """
        try:
            print(f"🧪 Testing web search with: '{test_query}'")
            
            results = self.search(test_query)
            
            if results:
                print("✅ Web search test successful")
                print(f"Results preview: {results[:200]}...")
                return True
            else:
                print("❌ Web search test failed")
                return False
                
        except Exception as e:
            print(f"❌ Web search test error: {e}")
            return False
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search system statistics."""
        return {
            'is_available': self.is_available,
            'api_key_configured': bool(self.api_key),
            'search_engine_id_configured': bool(self.search_engine_id),
            'max_results': self.max_results,
            'timeout': self.timeout,
            'base_url': self.base_url
        }