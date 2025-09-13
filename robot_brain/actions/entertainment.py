"""
🎭 Entertainment Module

Provides entertainment content including jokes, stories, and interactive activities.
Supports both Bangla and English content with cultural awareness.
"""

import random
import time
from typing import Dict, List, Optional

class EntertainmentModule:
    """
    🎭 Entertainment Module
    
    Provides entertainment content for the robot including:
    - Jokes and humor
    - Stories and tales
    - Interactive games
    - Cultural content
    """
    
    def __init__(self):
        """Initialize entertainment module."""
        self.bangla_jokes = self._load_bangla_jokes()
        self.english_jokes = self._load_english_jokes()
        self.bangla_stories = self._load_bangla_stories()
        self.english_stories = self._load_english_stories()
        self.riddles = self._load_riddles()
        
        print("✅ Entertainment module initialized")
    
    def _load_bangla_jokes(self) -> List[str]:
        """Load Bangla jokes."""
        return [
            "একজন লোক ডাক্তারের কাছে গিয়ে বলল, 'ডাক্তার, আমি ভুলে যাই সব কিছু।' ডাক্তার বললেন, 'কখন থেকে?' লোকটি বলল, 'কখন থেকে কি?'",
            
            "একজন শিক্ষক ছাত্রকে জিজ্ঞেস করলেন, 'পৃথিবীতে কতগুলো মহাদেশ আছে?' ছাত্র বলল, 'সাতটি।' শিক্ষক বললেন, 'ভুল।' ছাত্র বলল, 'তাহলে কতগুলো?' শিক্ষক বললেন, 'আমি জানি না, কিন্তু সাতটি নয়।'",
            
            "একজন লোক বাসে উঠে কন্ডাক্টরকে বলল, 'একটা টিকিট দিন।' কন্ডাক্টর বলল, 'কোথায় যাবেন?' লোকটি বলল, 'আমি জানি না।' কন্ডাক্টর বলল, 'তাহলে টিকিট দেবো কী করে?'",
            
            "একজন লোক রেস্তোরাঁয় গিয়ে বলল, 'একটা স্যান্ডউইচ দিন।' ওয়েটার বলল, 'কী ধরনের?' লোকটি বলল, 'খাবার ধরনের।'",
            
            "একজন লোক ফোনে বলল, 'হ্যালো, আমি কি সঠিক নম্বরে কথা বলছি?' অপর প্রান্ত থেকে উত্তর এল, 'না।' লোকটি বলল, 'তাহলে আমি ভুল নম্বরে কথা বলছি?' উত্তর এল, 'হ্যাঁ।'"
        ]
    
    def _load_english_jokes(self) -> List[str]:
        """Load English jokes."""
        return [
            "Why don't scientists trust atoms? Because they make up everything!",
            
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            
            "Why don't eggs tell jokes? They'd crack each other up!",
            
            "What do you call a fake noodle? An impasta!",
            
            "Why did the math book look so sad? Because it had too many problems!",
            
            "What do you call a bear with no teeth? A gummy bear!",
            
            "Why don't skeletons fight each other? They don't have the guts!",
            
            "What do you call a fish wearing a bowtie? So-fish-ticated!"
        ]
    
    def _load_bangla_stories(self) -> List[Dict[str, str]]:
        """Load Bangla stories."""
        return [
            {
                "title": "বুদ্ধিমান কাক",
                "story": "একদিন একটি কাক খুব তৃষ্ণার্ত ছিল। সে একটি কলসিতে পানি দেখতে পেল কিন্তু পানি এত নিচে ছিল যে তার ঠোঁট পৌঁছাতে পারছিল না। তখন সে চারপাশে ছোট ছোট পাথর খুঁজে বের করল এবং কলসিতে ফেলতে লাগল। পাথর ফেলতে ফেলতে পানি উপরে উঠে এল এবং কাক তৃষ্ণা মেটাতে পারল।"
            },
            {
                "title": "সৎ কাঠুরে",
                "story": "একজন গরিব কাঠুরে বনে গিয়ে কাঠ কাটছিল। হঠাৎ তার কুড়াল নদীতে পড়ে গেল। তিনি কাঁদতে লাগলেন। তখন একজন দেবতা এসে তাকে সোনার কুড়াল দিলেন। কাঠুরে বললেন, 'এটা আমার নয়।' দেবতা তাকে রুপার কুড়াল দিলেন। কাঠুরে আবার বললেন, 'এটাও আমার নয়।' শেষে দেবতা তার আসল কুড়াল দিলেন। কাঠুরে খুশি হয়ে বললেন, 'এটাই আমার কুড়াল।' দেবতা তার সততার জন্য তাকে তিনটি কুড়ালই দান করলেন।"
            }
        ]
    
    def _load_english_stories(self) -> List[Dict[str, str]]:
        """Load English stories."""
        return [
            {
                "title": "The Wise Crow",
                "story": "A thirsty crow found a pitcher with water, but the water was too low for his beak to reach. He looked around and found small stones. He started dropping stones into the pitcher one by one. As he dropped more stones, the water level rose until he could drink and quench his thirst."
            },
            {
                "title": "The Honest Woodcutter",
                "story": "A poor woodcutter was cutting wood in the forest when his axe fell into a river. He started crying. A god appeared and offered him a golden axe. The woodcutter said, 'That's not mine.' The god offered a silver axe. The woodcutter again said, 'That's not mine either.' Finally, the god gave him his original axe. The woodcutter happily said, 'That's my axe!' The god was pleased with his honesty and gave him all three axes."
            }
        ]
    
    def _load_riddles(self) -> List[Dict[str, str]]:
        """Load riddles in both languages."""
        return [
            {
                "question_bn": "এমন কি জিনিস যা খেলে বাড়ে, না খেলে কমে?",
                "answer_bn": "আগুন",
                "question_en": "What grows when you feed it but dies when you give it water?",
                "answer_en": "Fire"
            },
            {
                "question_bn": "এমন কি জিনিস যা সবসময় আসে কিন্তু কখনো যায় না?",
                "answer_bn": "আগামীকাল",
                "question_en": "What always comes but never arrives?",
                "answer_en": "Tomorrow"
            },
            {
                "question_bn": "এমন কি জিনিস যা ভাঙলে বেশি কাজ করে?",
                "answer_bn": "রেকর্ড",
                "question_en": "What works better when it's broken?",
                "answer_en": "Record"
            }
        ]
    
    def get_general_content(self, language: str = 'en') -> str:
        """
        Get general entertainment content.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Entertainment content
        """
        try:
            content_type = random.choice(['joke', 'story', 'riddle'])
            
            if content_type == 'joke':
                return self.get_joke(language)
            elif content_type == 'story':
                return self.get_story(language)
            else:
                return self.get_riddle(language)
                
        except Exception as e:
            print(f"❌ Entertainment content error: {e}")
            return self._get_fallback_content(language)
    
    def get_joke(self, language: str = 'en') -> str:
        """
        Get a random joke.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Joke text
        """
        try:
            if language == 'bn':
                jokes = self.bangla_jokes
                intro = "একটা মজার কৌতুক শুনুন:"
            else:
                jokes = self.english_jokes
                intro = "Here's a funny joke:"
            
            if jokes:
                joke = random.choice(jokes)
                return f"{intro}\n\n{joke}"
            else:
                return self._get_fallback_joke(language)
                
        except Exception as e:
            print(f"❌ Joke error: {e}")
            return self._get_fallback_joke(language)
    
    def get_story(self, language: str = 'en') -> str:
        """
        Get a random story.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Story text
        """
        try:
            if language == 'bn':
                stories = self.bangla_stories
                intro = "একটা গল্প শুনুন:"
            else:
                stories = self.english_stories
                intro = "Here's a story for you:"
            
            if stories:
                story = random.choice(stories)
                return f"{intro}\n\n📖 {story['title']}\n\n{story['story']}"
            else:
                return self._get_fallback_story(language)
                
        except Exception as e:
            print(f"❌ Story error: {e}")
            return self._get_fallback_story(language)
    
    def get_riddle(self, language: str = 'en') -> str:
        """
        Get a random riddle.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Riddle text
        """
        try:
            if self.riddles:
                riddle = random.choice(self.riddles)
                
                if language == 'bn':
                    question = riddle['question_bn']
                    answer = riddle['answer_bn']
                    intro = "একটা ধাঁধা:"
                else:
                    question = riddle['question_en']
                    answer = riddle['answer_en']
                    intro = "Here's a riddle for you:"
                
                return f"{intro}\n\n❓ {question}\n\n💡 উত্তর: {answer}" if language == 'bn' else f"{intro}\n\n❓ {question}\n\n💡 Answer: {answer}"
            else:
                return self._get_fallback_riddle(language)
                
        except Exception as e:
            print(f"❌ Riddle error: {e}")
            return self._get_fallback_riddle(language)
    
    def get_student_content(self, language: str = 'en') -> str:
        """
        Get entertainment content appropriate for students.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Student-appropriate content
        """
        try:
            content_type = random.choice(['joke', 'story', 'riddle'])
            
            if content_type == 'joke':
                return self.get_joke(language)
            elif content_type == 'story':
                return self.get_educational_story(language)
            else:
                return self.get_riddle(language)
                
        except Exception as e:
            print(f"❌ Student content error: {e}")
            return self._get_fallback_content(language)
    
    def get_professional_content(self, language: str = 'en') -> str:
        """
        Get entertainment content appropriate for teachers/principals.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Professional-appropriate content
        """
        try:
            if language == 'bn':
                return "আজকের দিনটি আপনার জন্য শুভ হোক! শিক্ষা হলো আলোর পথ। আপনি ছাত্রদের জীবনে আলো ছড়াচ্ছেন।"
            else:
                return "Have a wonderful day! Education is the light of life. You are spreading light in your students' lives."
                
        except Exception as e:
            print(f"❌ Professional content error: {e}")
            return self._get_fallback_content(language)
    
    def get_educational_story(self, language: str = 'en') -> str:
        """
        Get an educational story.
        
        Args:
            language: Language code ('bn' or 'en')
            
        Returns:
            Educational story
        """
        try:
            if language == 'bn':
                return "📚 শিক্ষামূলক গল্প:\n\nএকজন ছাত্র প্রতিদিন একটু একটু করে পড়াশোনা করত। তার বন্ধুরা তাকে বলত, 'এত কম পড়লে কী হবে?' কিন্তু সে বলত, 'ধীরে ধীরে পড়লে ভালোভাবে মনে থাকে।' এক বছর পর সে সবচেয়ে ভালো ফলাফল করল। নৈতিকতা: ধৈর্য এবং নিয়মিত চেষ্টা সফলতার চাবিকাঠি।"
            else:
                return "📚 Educational Story:\n\nA student studied a little bit every day. His friends said, 'What's the point of studying so little?' But he replied, 'Studying slowly helps me remember better.' After one year, he achieved the best results. Moral: Patience and regular effort are the keys to success."
                
        except Exception as e:
            print(f"❌ Educational story error: {e}")
            return self._get_fallback_story(language)
    
    def _get_fallback_content(self, language: str) -> str:
        """Get fallback content when other content fails."""
        if language == 'bn':
            return "দুঃখিত, এখন কোনো বিনোদনমূলক বিষয়বস্তু নেই। পরে আবার চেষ্টা করুন।"
        else:
            return "Sorry, no entertainment content available right now. Please try again later."
    
    def _get_fallback_joke(self, language: str) -> str:
        """Get fallback joke."""
        if language == 'bn':
            return "একটা মজার কথা: রোবটরা কখনো ক্লান্ত হয় না, কিন্তু তারা সবসময় চার্জ নেয়!"
        else:
            return "Here's a funny fact: Robots never get tired, but they always need to recharge!"
    
    def _get_fallback_story(self, language: str) -> str:
        """Get fallback story."""
        if language == 'bn':
            return "একটা ছোট গল্প: একদিন একটি রোবট মানুষের মতো কথা বলতে শিখল। সে বলল, 'আমি তোমাদের বন্ধু হতে চাই।'"
        else:
            return "A short story: One day, a robot learned to speak like humans. It said, 'I want to be your friend.'"
    
    def _get_fallback_riddle(self, language: str) -> str:
        """Get fallback riddle."""
        if language == 'bn':
            return "একটা ধাঁধা: এমন কি জিনিস যা সবসময় আসে কিন্তু কখনো যায় না? উত্তর: আগামীকাল।"
        else:
            return "Here's a riddle: What always comes but never arrives? Answer: Tomorrow."
    
    def get_entertainment_stats(self) -> Dict[str, int]:
        """Get entertainment content statistics."""
        return {
            'bangla_jokes': len(self.bangla_jokes),
            'english_jokes': len(self.english_jokes),
            'bangla_stories': len(self.bangla_stories),
            'english_stories': len(self.english_stories),
            'riddles': len(self.riddles)
        }