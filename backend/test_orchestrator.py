#!/usr/bin/env python3
"""
Complete test script for the e-commerce bot
Run this to test all functionality
"""

import requests
import json
import time
from typing import Dict, Any

class EcommerceBotTester:
    def __init__(self, base_url: str = "http://localhost:9002"):
        self.base_url = base_url
        self.test_phone = "+1234567890"
        self.test_results = []
    
    def test_endpoint(self, name: str, method: str, endpoint: str, data: Dict = None, expected_success: bool = True) -> bool:
        """Test a single endpoint"""
        print(f"\n🧪 Testing: {name}")
        print(f"📡 {method} {endpoint}")
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                if endpoint == "/process-text":
                    response = requests.post(url, json=data)
                else:
                    response = requests.post(url, data=data)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {json.dumps(result, indent=2)[:200]}...")
                
                if expected_success:
                    if result.get("success", True):  # Some endpoints don't have success field
                        print("✅ Test PASSED")
                        self.test_results.append((name, "PASS"))
                        return True
                    else:
                        print(f"❌ Test FAILED: {result}")
                        self.test_results.append((name, "FAIL"))
                        return False
                else:
                    print("✅ Test PASSED (expected failure)")
                    self.test_results.append((name, "PASS"))
                    return True
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append((name, "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.test_results.append((name, "ERROR"))
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting E-commerce Bot Test Suite")
        print("=" * 50)
        
        # Test 1: Health Check
        self.test_endpoint(
            "Health Check",
            "GET",
            "/health"
        )
        
        # Test 2: List Products
        self.test_endpoint(
            "List Products",
            "GET",
            "/products"
        )
        
        # Test 3: Search Products (Text)
        self.test_endpoint(
            "Search Products",
            "POST",
            "/process-text",
            {"message": "I want to buy a phone", "customer_phone": self.test_phone}
        )
        
        # Test 4: Add to Cart
        self.test_endpoint(
            "Add to Cart",
            "POST",
            "/process-text",
            {"message": "add iphone to cart", "customer_phone": self.test_phone}
        )
        
        # Test 5: View Cart
        self.test_endpoint(
            "View Cart",
            "POST",
            "/process-text",
            {"message": "show my cart", "customer_phone": self.test_phone}
        )
        
        # Test 6: Direct Cart API
        self.test_endpoint(
            "Direct Cart API",
            "GET",
            f"/customer/{self.test_phone}/cart"
        )
        
        # Test 7: Order Status
        self.test_endpoint(
            "Check Orders",
            "POST",
            "/process-text",
            {"message": "my orders", "customer_phone": self.test_phone}
        )
        
        # Test 8: Chat Response
        self.test_endpoint(
            "Chat Response",
            "POST",
            "/process-text",
            {"message": "hello", "customer_phone": self.test_phone}
        )
        
        # Test 9: Place Order
        self.test_endpoint(
            "Place Order",
            "POST",
            "/process-text",
            {"message": "order to 123 Main Street", "customer_phone": self.test_phone}
        )
        
        # Test 10: Invalid Request
        self.test_endpoint(
            "Invalid Request",
            "POST",
            "/process-text",
            {"message": "blah blah nonsense", "customer_phone": self.test_phone}
        )
        
        # Print Results
        self.print_results()
    
    def test_conversation_flow(self):
        """Test a complete conversation flow"""
        print("\n🗣️ Testing Conversation Flow")
        print("=" * 50)
        
        conversation = [
            "hello",
            "I want to buy a laptop",
            "add macbook to cart",
            "show my cart",
            "checkout to 456 Oak Street",
            "check my orders"
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"\n👤 Message {i}: '{message}'")
            success = self.test_endpoint(
                f"Conversation Step {i}",
                "POST",
                "/process-text",
                {"message": message, "customer_phone": f"+conv{int(time.time())}"}
            )
            
            if not success:
                print(f"❌ Conversation failed at step {i}")
                break
            
            time.sleep(1)  # Small delay between messages
    
    def test_llm_intents(self):
        """Test specific LLM intent detection"""
        print("\n🧠 Testing LLM Intent Detection")
        print("=" * 50)
        
        intent_tests = [
            ("search", "find me some headphones"),
            ("search", "looking for wireless mouse"),
            ("add", "add samsung phone to my cart"),
            ("add", "put 2 keyboards in cart"),
            ("cart", "what's in my basket"),
            ("cart", "show cart contents"),
            ("order", "checkout to 789 Pine Ave"),
            ("status", "what are my recent orders"),
            ("chat", "how are you today"),
            ("chat", "thank you")
        ]
        
        for intent, message in intent_tests:
            print(f"\n🎯 Testing intent '{intent}': '{message}'")
            self.test_endpoint(
                f"Intent: {intent}",
                "POST",
                "/process-text",
                {"message": message, "customer_phone": f"+intent{int(time.time())}"}
            )
            time.sleep(0.5)
    
    def print_results(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL") 
        errors = sum(1 for _, result in self.test_results if result == "ERROR")
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status_emoji = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            print(f"{status_emoji} {test_name}: {result}")
        
        print(f"\n📈 SUMMARY:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"⚠️ Errors: {errors}/{total}")
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 GREAT! System is working well!")
        elif success_rate >= 60:
            print("⚠️ OKAY. Some issues need fixing.")
        else:
            print("❌ POOR. Major issues detected.")

def main():
    """Main test function"""
    print("🤖 E-commerce Bot Tester v3.0")
    print("Make sure your server is running on localhost:9002")
    print()
    
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
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return
    
    tester = EcommerceBotTester()
    
    # Run different test suites
    tester.run_all_tests()
    tester.test_conversation_flow()
    tester.test_llm_intents()
    
    print("\n🏁 All tests completed!")

if __name__ == "__main__":
    main()