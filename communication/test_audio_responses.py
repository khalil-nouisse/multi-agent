#!/usr/bin/env python3
"""
Test script for audio response functionality
"""

import requests
import json
import base64
import os
from typing import Dict

class AudioResponseTester:
    def __init__(self, base_url: str = "http://localhost:9002"):
        self.base_url = base_url
        self.test_phone = "+audio_test"
    
    def test_health_with_audio(self):
        """Test health check to see TTS status"""
        print("🏥 Testing health check...")
        
        response = requests.get(f"{self.base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"🔊 TTS Method: {data['components']['tts_method']}")
            return data['components']['tts_method'] != 'none'
        return False
    
    def test_tts_endpoint(self):
        """Test the TTS test endpoint"""
        print("\n🧪 Testing TTS endpoint...")
        
        response = requests.get(f"{self.base_url}/test-tts?text=Hello, this is a test of text to speech!")
        
        if response.status_code == 200:
            # Save the audio file
            with open("test_tts_output.mp3", "wb") as f:
                f.write(response.content)
            print("✅ TTS test successful! Saved as test_tts_output.mp3")
            return True
        else:
            print(f"❌ TTS test failed: {response.status_code}")
            return False
    
    def test_text_with_audio_response(self):
        """Test text input with audio response"""
        print("\n💬 Testing text with audio response...")
        
        data = {
            "message": "show my cart",
            "customer_phone": self.test_phone,
            "return_audio": True
        }
        
        response = requests.post(f"{self.base_url}/process-text", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Text processed: {result['response'][:50]}...")
            
            if "audio_response" in result:
                # Decode and save audio
                audio_bytes = base64.b64decode(result["audio_response"])
                with open("text_response_audio.mp3", "wb") as f:
                    f.write(audio_bytes)
                print("🔊 Audio response saved as text_response_audio.mp3")
                return True
            else:
                print("⚠️ No audio response in result")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    
    def test_text_audio_file_endpoint(self):
        """Test text input with audio file response"""
        print("\n📁 Testing text with audio file response...")
        
        data = {
            "message": "find me some headphones",
            "customer_phone": self.test_phone
        }
        
        response = requests.post(f"{self.base_url}/process-text-audio-file", data=data)
        
        if response.status_code == 200:
            # Save the audio file
            with open("search_response_audio.mp3", "wb") as f:
                f.write(response.content)
            print("✅ Audio file response saved as search_response_audio.mp3")
            return True
        else:
            print(f"❌ Audio file request failed: {response.status_code}")
            return False
    
    def test_conversation_with_audio(self):
        """Test a full conversation with audio responses"""
        print("\n🗣️ Testing conversation flow with audio...")
        
        conversation = [
            "hello",
            "I want to buy a laptop", 
            "add macbook to cart",
            "show my cart"
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"\n👤 Step {i}: '{message}'")
            
            data = {
                "message": message,
                "customer_phone": f"+conv_audio_{i}",
                "return_audio": True
            }
            
            response = requests.post(f"{self.base_url}/process-text", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"🤖 Response: {result['response'][:80]}...")
                
                if "audio_response" in result:
                    # Save audio response
                    audio_bytes = base64.b64decode(result["audio_response"])
                    filename = f"conversation_step_{i}_audio.mp3"
                    with open(filename, "wb") as f:
                        f.write(audio_bytes)
                    print(f"🔊 Audio saved: {filename}")
                else:
                    print("⚠️ No audio in response")
            else:
                print(f"❌ Step {i} failed: {response.status_code}")
                break
    
    def run_all_audio_tests(self):
        """Run all audio response tests"""
        print("🎵 Audio Response Test Suite")
        print("=" * 50)
        
        # Check if TTS is available
        if not self.test_health_with_audio():
            print("❌ TTS not available. Install gtts or pyttsx3:")
            print("pip install gtts")
            print("pip install pyttsx3")
            return
        
        tests = [
            ("TTS Endpoint", self.test_tts_endpoint),
            ("Text with Audio Response", self.test_text_with_audio_response),
            ("Text Audio File Response", self.test_text_audio_file_endpoint),
            ("Conversation with Audio", self.test_conversation_with_audio)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        print(f"\n📊 Audio Tests: {passed}/{total} passed")
        
        if passed > 0:
            print(f"\n🎵 Audio files generated:")
            audio_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
            for file in audio_files:
                print(f"  • {file}")

def main():
    """Main test function"""
    print("🎵 Audio Response Tester v1.0")
    print("Make sure your server is running on localhost:9002")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:9002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server responded but with error")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running! Start it first with: python main.py")
        return
    
    tester = AudioResponseTester()
    tester.run_all_audio_tests()
    
    print("\n🏁 Audio tests completed!")

if __name__ == "__main__":
    main()