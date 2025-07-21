from openai import OpenAI
import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

class LLMOrchestrator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.api_key = api_key
    
    def get_conversation_context(self, conversation_history: List[Dict]) -> str:
        """Get recent conversation context (last 3 messages)"""
        if not conversation_history:
            return ""
        
        recent_history = conversation_history[-3:]
        context = "Recent conversation:\n"
        for msg in recent_history:
            context += f"Customer: {msg['message']}\nBot: {msg['response']}\n"
        return context
    
    def process_message(self, message: str, customer_id: int, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Process customer message and determine intent"""
        
        context = self.get_conversation_context(conversation_history)
        
        system_prompt = f"""You are a smart e-commerce assistant. Read the customer message and respond with EXACTLY one of these formats:

SEARCH:keyword - when customer wants to find/buy products
ADD:product:quantity - when customer wants to add items to cart
CART - when customer wants to see their cart/basket
REMOVE:id - when customer wants to remove items
ORDER:address - when customer wants to checkout/place order
STATUS - when customer wants to check their orders
CHAT:response - for greetings and general talk

STRICT MATCHING RULES:
- Any mention of "cart", "basket", "show", "view", "what's in" = CART
- Any mention of "orders", "my orders", "order status", "check orders" = STATUS
- Any mention of "find", "want", "buy", "need", "search", "looking" = SEARCH:keyword
- Any mention of "show all", "all products", "what do you have", "list products" = SEARCH:all
- Any mention of "add", "put in cart" = ADD:product:1
- Any mention of "checkout", "order to", "place order" = ORDER:address
- Greetings like "hello", "hi", "thanks" = CHAT:response

EXAMPLES:
"show my cart" → CART
"what's in my cart" → CART
"view my basket" → CART
"my orders" → STATUS
"check my orders" → STATUS
"order status" → STATUS
"I want a phone" → SEARCH:phone
"find headphones" → SEARCH:headphones
"show me all products" → SEARCH:all
"what do you have" → SEARCH:all
"list all products" → SEARCH:all
"show everything" → SEARCH:all
"add iphone" → ADD:iphone:1
"checkout to 123 Main St" → ORDER:123 Main St
"hello" → CHAT:Hi! Welcome! What can I help you find?

{context}

Customer message: "{message}"

Your response (format only):"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.0,  # Zero temperature for consistent results
                max_tokens=50     # Short responses only
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"🧠 LLM Response: {response_text}")
            
            # Parse the response
            if response_text.startswith("SEARCH:"):
                query = response_text.replace("SEARCH:", "").strip()
                return {
                    "type": "function_call",
                    "function": "search_products",
                    "arguments": {"query": query},
                    "message": ""
                }
            
            elif response_text.startswith("ADD:"):
                content = response_text.replace("ADD:", "").strip()
                if ":" in content:
                    parts = content.split(":", 1)
                    product_name = parts[0].strip()
                    quantity = int(parts[1].strip()) if parts[1].strip().isdigit() else 1
                else:
                    product_name = content
                    quantity = 1
                
                return {
                    "type": "function_call",
                    "function": "add_to_cart_by_name",
                    "arguments": {"product_name": product_name, "quantity": quantity},
                    "message": ""
                }
            
            elif response_text == "CART":
                return {
                    "type": "function_call",
                    "function": "view_cart",
                    "arguments": {},
                    "message": ""
                }
            
            elif response_text.startswith("REMOVE:"):
                product_id_str = response_text.replace("REMOVE:", "").strip()
                product_id = int(product_id_str) if product_id_str.isdigit() else None
                
                if not product_id:
                    return {
                        "type": "text_response",
                        "response": "Please specify which item to remove by saying 'remove item [number]'",
                        "function": None,
                        "arguments": {}
                    }
                
                return {
                    "type": "function_call",
                    "function": "remove_from_cart",
                    "arguments": {"product_id": product_id},
                    "message": ""
                }
            
            elif response_text.startswith("ORDER:"):
                address = response_text.replace("ORDER:", "").strip()
                if not address:
                    return {
                        "type": "text_response",
                        "response": "Please provide your delivery address to place the order.",
                        "function": None,
                        "arguments": {}
                    }
                
                return {
                    "type": "function_call",
                    "function": "confirm_order",
                    "arguments": {"delivery_address": address},
                    "message": ""
                }
            
            elif response_text == "STATUS":
                return {
                    "type": "function_call",
                    "function": "check_order_status",
                    "arguments": {},
                    "message": ""
                }
            
            elif response_text.startswith("CHAT:"):
                chat_response = response_text.replace("CHAT:", "").strip()
                return {
                    "type": "text_response",
                    "response": chat_response,
                    "function": None,
                    "arguments": {}
                }
            
            else:
                # If format is not recognized, default to chat
                return {
                    "type": "text_response",
                    "response": "I'm not sure how to help with that. Try asking to search for products, view your cart, or place an order.",
                    "function": None,
                    "arguments": {}
                }
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "type": "text_response",
                "response": "I'm having trouble understanding. Can you try rephrasing your request?",
                "function": None,
                "arguments": {}
            }
    
    def generate_function_response(self, function_result: Any, original_message: str) -> str:
        """Generate natural language response based on function result"""
        
        try:
            print(f"📝 Generating response for: {type(function_result)}")
            print(f"📝 Function result content: {function_result}")
            
            # Handle different result types
            if isinstance(function_result, dict):
                # Handle error cases
                if function_result.get("success") is False:
                    return f"❌ {function_result.get('message', 'Something went wrong')}"
                
                # Handle cart view
                if "items" in function_result and "total" in function_result:
                    if not function_result["items"]:
                        return "🛒 Your cart is empty!\n\nTell me what you're looking for and I'll help you find it!"
                    
                    response = "🛒 **Your Cart:**\n\n"
                    for i, item in enumerate(function_result["items"], 1):
                        response += f"{i}. {item['name']} - ${item['price']:.2f} x {item['quantity']} = ${item['subtotal']:.2f}\n"
                    
                    response += f"\n💳 **Total: ${function_result['total']:.2f}**\n"
                    response += f"📦 **{function_result['count']} items**\n\n"
                    response += "Ready to order? Send me your delivery address!"
                    return response
                
                # Handle order status
                elif "orders" in function_result:
                    if not function_result["orders"]:
                        return "📋 No orders found.\n\nWant to start shopping? Just tell me what you need!"
                    
                    response = "📋 **Your Orders:**\n\n"
                    for order in function_result["orders"]:
                        status_emoji = "⏳" if order['status'] == 'pending' else "✅"
                        response += f"{status_emoji} Order #{order['order_id']} - ${order['total']:.2f}\n"
                        response += f"📅 {order['created_at']}\n"
                        response += f"📍 {order.get('delivery_address', 'No address')}\n\n"
                    return response
                
                # Handle success messages
                elif "message" in function_result:
                    message = function_result["message"]
                    if "added" in message.lower():
                        return f"✅ {message}\n\n🛒 Want to see your cart or continue shopping?"
                    elif "order" in message.lower() and "placed" in message.lower():
                        return f"🎉 {message}\n\n📦 Your order is being processed!"
                    else:
                        return f"✅ {message}"
            
            # Handle list and tuple results (product search) - FIXED THIS PART
            elif isinstance(function_result, (list, tuple)):
                # Convert tuple to list if needed
                products = list(function_result) if isinstance(function_result, tuple) else function_result
                
                if not products:
                    return "🔍 No products found.\n\nTry a different search term or ask to see all our products!"
                
                response = f"🔍 **Found {len(products)} products:**\n\n"
                for i, product in enumerate(products[:5], 1):
                    # Handle both dict and tuple formats
                    if isinstance(product, dict):
                        name = product.get('name', 'Unknown')
                        price = product.get('price', 0)
                        stock = product.get('stock_quantity', 'N/A')
                    else:
                        # If it's a raw database row, handle it
                        name = str(product)
                        price = 0
                        stock = 'N/A'
                    
                    response += f"{i}. **{name}** - ${price:.2f}\n"
                    response += f"   📦 Stock: {stock}\n\n"
                
                if len(products) > 5:
                    response += f"...and {len(products) - 5} more.\n\n"
                
                response += "💡 Say 'add [product name]' to add to cart!"
                return response
            
            return "✅ Done! How else can I help?"
            
        except Exception as e:
            print(f"Response generation error: {e}")
            import traceback
            traceback.print_exc()
            return "✅ Request processed! What else can I help you with?"