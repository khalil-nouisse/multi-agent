import os
import tempfile
import time
from typing import Optional, Union
import io
import base64

class AudioResponseProcessor:
    def __init__(self):
        """Initialize TTS processor with multiple options"""
        self.temp_dir = tempfile.gettempdir()
        
        # Try to load TTS libraries
        self.tts_method = self._detect_tts_method()
        print(f"🔊 TTS Method: {self.tts_method}")
    
    def _detect_tts_method(self) -> str:
        """Detect available TTS method"""
        try:
            # Option 1: OpenAI TTS (best quality)
            import openai
            return "openai"
        except ImportError:
            pass
        
        try:
            # Option 2: gTTS (Google TTS - free)
            import gtts
            return "gtts"
        except ImportError:
            pass
        
        try:
            # Option 3: pyttsx3 (offline TTS)
            import pyttsx3
            return "pyttsx3"
        except ImportError:
            pass
        
        return "none"
    
    def text_to_speech_openai(self, text: str, api_key: str) -> Optional[bytes]:
        """Convert text to speech using OpenAI TTS (best quality)"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            response = client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice="alloy",  # alloy, echo, fable, onyx, nova, shimmer
                input=clean_text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            print(f"❌ OpenAI TTS error: {e}")
            return None
    
    def text_to_speech_gtts(self, text: str) -> Optional[bytes]:
        """Convert text to speech using Google TTS (free)"""
        try:
            from gtts import gTTS
            
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            # Create gTTS object
            tts = gTTS(text=clean_text, lang='en', slow=False)
            
            # Save to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            print(f"❌ gTTS error: {e}")
            return None
    
    def text_to_speech_pyttsx3(self, text: str) -> Optional[bytes]:
        """Convert text to speech using pyttsx3 (offline)"""
        try:
            import pyttsx3
            
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            # Create unique temp file
            timestamp = str(int(time.time() * 1000))
            temp_file = os.path.join(self.temp_dir, f"tts_audio_{timestamp}.wav")
            
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Set properties (optional)
            engine.setProperty('rate', 150)    # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level
            
            # Save to file
            engine.save_to_file(clean_text, temp_file)
            engine.runAndWait()
            
            # Read file and return bytes
            if os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up temp file
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                return audio_data
            
            return None
            
        except Exception as e:
            print(f"❌ pyttsx3 error: {e}")
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation"""
        # Remove emojis and special characters
        import re
        
        # Remove emojis
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                 u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 "]+", flags=re.UNICODE)
        
        clean_text = emoji_pattern.sub(r'', text)
        
        # Remove markdown formatting
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)  # Bold
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)      # Italic
        
        # Replace common symbols with words
        replacements = {
            '$': 'dollars ',
            '#': 'number ',
            '&': 'and ',
            '%': 'percent ',
            '💳': 'Total: ',
            '📦': '',
            '🛒': 'Cart: ',
            '📋': 'Orders: ',
            '🔍': 'Found: ',
            '✅': '',
            '❌': 'Error: ',
            '🎉': 'Great! ',
            '📅': '',
            '📍': 'Address: '
        }
        
        for symbol, replacement in replacements.items():
            clean_text = clean_text.replace(symbol, replacement)
        
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Limit length (TTS services have limits)
        if len(clean_text) > 4000:
            clean_text = clean_text[:4000] + "..."
        
        return clean_text
    
    def generate_audio_response(self, text: str, api_key: str = None) -> Optional[bytes]:
        """Generate audio response using available TTS method"""
        print(f"🔊 Converting to audio: '{text[:50]}...'")
        
        if self.tts_method == "openai" and api_key:
            return self.text_to_speech_openai(text, api_key)
        
        elif self.tts_method == "gtts":
            return self.text_to_speech_gtts(text)
        
        elif self.tts_method == "pyttsx3":
            return self.text_to_speech_pyttsx3(text)
        
        else:
            print("❌ No TTS method available")
            return None
    
    def save_audio_to_file(self, audio_bytes: bytes, filename: str = None) -> str:
        """Save audio bytes to file and return path"""
        if not filename:
            timestamp = str(int(time.time() * 1000))
            filename = f"response_audio_{timestamp}.mp3"
        
        file_path = os.path.join(self.temp_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(audio_bytes)
        
        print(f"💾 Audio saved: {file_path}")
        return file_path
    
    def audio_to_base64(self, audio_bytes: bytes) -> str:
        """Convert audio bytes to base64 string"""
        return base64.b64encode(audio_bytes).decode('utf-8')