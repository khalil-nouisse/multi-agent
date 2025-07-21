import pymysql
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, host='localhost', user='root', password='king7ussin', database='whatsapp_ecommerce'):
        self.connection_params = {
            'host': host,
            'user': user, 
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'autocommit': True
        }
        print(f"🗄️ Database initialized: {database}")
    
    def get_connection(self):
        try:
            conn = pymysql.connect(**self.connection_params)
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        connection = self.get_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                print(f"📊 Query executed: {len(result)} rows returned")
                return result
        except Exception as e:
            print(f"❌ Query error: {e}")
            raise
        finally:
            connection.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                result = cursor.execute(query, params or ())
                last_id = cursor.lastrowid if 'INSERT' in query.upper() else result
                print(f"📝 Update executed: {result} rows affected, last_id: {last_id}")
                return last_id
        except Exception as e:
            print(f"❌ Update error: {e}")
            raise
        finally:
            connection.close()

class EcommerceFunctions:
    def __init__(self):
        self.db = DatabaseManager()
        print("✅ EcommerceFunctions initialized")
    
    def get_or_create_customer(self, phone_number: str) -> Dict:
        """Get existing customer or create new one"""
        try:
            print(f"👤 Getting customer: {phone_number}")
            
            # Check if customer exists
            customers = self.db.execute_query(
                "SELECT * FROM customers WHERE phone_number = %s", 
                (phone_number,)
            )
            
            if customers:
                print(f"✅ Found existing customer: {customers[0]['id']}")
                return customers[0]
            
            # Create new customer
            customer_id = self.db.execute_update(
                "INSERT INTO customers (phone_number, created_at) VALUES (%s, %s)",
                (phone_number, datetime.now())
            )
            
            print(f"✅ Created new customer: {customer_id}")
            return {
                'id': customer_id,
                'phone_number': phone_number,
                'name': None,
                'address': None,
                'created_at': datetime.now()
            }
        except Exception as e:
            print(f"❌ Error in get_or_create_customer: {e}")
            raise
    
    def search_products(self, query: str = "", category: str = None, max_price: float = None) -> List[Dict]:
        """Search for products"""
        try:
            print(f"🔍 Searching products: '{query}', category: {category}, max_price: {max_price}")
            
            sql = "SELECT * FROM products WHERE 1=1"
            params = []
            
            if query:
                words = query.lower().split()
                search_conditions = []
                for word in words:
                    search_conditions.append("(LOWER(name) LIKE %s OR LOWER(description) LIKE %s)")
                    params.extend([f"%{word}%", f"%{word}%"])
                
                if search_conditions:
                    sql += " AND (" + " AND ".join(search_conditions) + ")"
            
            if category:
                sql += " AND category = %s"
                params.append(category)
            
            if max_price:
                sql += " AND price <= %s"
                params.append(max_price)
            
            sql += " ORDER BY name LIMIT 20"
            
            products = self.db.execute_query(sql, tuple(params))
            print(f"✅ Found {len(products)} products")
            return products
            
        except Exception as e:
            print(f"❌ Error in search_products: {e}")
            return []
    
    def find_product_by_name(self, product_name: str) -> Optional[Dict]:
        """Find a product by name with fuzzy matching"""
        try:
            print(f"🔍 Finding product by name: '{product_name}'")
            
            # First try exact match
            products = self.db.execute_query(
                "SELECT * FROM products WHERE LOWER(name) = %s", 
                (product_name.lower(),)
            )
            
            if products:
                print(f"✅ Found exact match: {products[0]['name']}")
                return products[0]
            
            # Try partial match
            products = self.db.execute_query(
                "SELECT * FROM products WHERE LOWER(name) LIKE %s ORDER BY name LIMIT 1", 
                (f"%{product_name.lower()}%",)
            )
            
            if products:
                print(f"✅ Found partial match: {products[0]['name']}")
                return products[0]
            
            print(f"❌ No product found for: '{product_name}'")
            return None
            
        except Exception as e:
            print(f"❌ Error in find_product_by_name: {e}")
            return None
    
    def add_to_cart_by_name(self, customer_id: int, product_name: str, quantity: int = 1) -> Dict[str, Any]:
        """Add product to cart by name"""
        try:
            print(f"🛒 Adding to cart: customer={customer_id}, product='{product_name}', qty={quantity}")
            
            # Find the product
            product = self.find_product_by_name(product_name)
            
            if not product:
                # Try to search for similar products
                similar_products = self.search_products(product_name)
                if similar_products:
                    product_list = [f"• {p['name']}" for p in similar_products[:3]]
                    return {
                        "success": False, 
                        "message": f"'{product_name}' not found. Did you mean:\n" + "\n".join(product_list)
                    }
                else:
                    return {"success": False, "message": f"Product '{product_name}' not found"}
            
            return self.add_to_cart(customer_id, product['id'], quantity)
            
        except Exception as e:
            print(f"❌ Error in add_to_cart_by_name: {e}")
            return {"success": False, "message": "Error adding to cart"}
    
    def add_to_cart(self, customer_id: int, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Add product to cart by ID"""
        try:
            print(f"🛒 Adding to cart: customer={customer_id}, product_id={product_id}, qty={quantity}")
            
            # Check if product exists and has stock
            products = self.db.execute_query(
                "SELECT * FROM products WHERE id = %s", 
                (product_id,)
            )
            
            if not products:
                return {"success": False, "message": "Product not found"}
            
            product = products[0]
            
            if product['stock_quantity'] < quantity:
                return {"success": False, "message": f"Only {product['stock_quantity']} items available"}
            
            # Check if item already in cart
            existing = self.db.execute_query(
                "SELECT * FROM cart WHERE customer_id = %s AND product_id = %s",
                (customer_id, product_id)
            )
            
            if existing:
                # Update quantity
                new_quantity = existing[0]['quantity'] + quantity
                if product['stock_quantity'] < new_quantity:
                    return {"success": False, "message": f"Cannot add {quantity} more. Total would exceed stock."}
                
                self.db.execute_update(
                    "UPDATE cart SET quantity = %s WHERE customer_id = %s AND product_id = %s",
                    (new_quantity, customer_id, product_id)
                )
                total_quantity = new_quantity
            else:
                # Add new cart item
                self.db.execute_update(
                    "INSERT INTO cart (customer_id, product_id, quantity, added_at) VALUES (%s, %s, %s, %s)",
                    (customer_id, product_id, quantity, datetime.now())
                )
                total_quantity = quantity
            
            print(f"✅ Added to cart successfully")
            return {
                "success": True,
                "message": f"Added {quantity} x {product['name']} to cart",
                "product": product['name'],
                "quantity": quantity,
                "total_quantity": total_quantity,
                "price": float(product['price'])
            }
            
        except Exception as e:
            print(f"❌ Error in add_to_cart: {e}")
            return {"success": False, "message": "Error adding to cart"}
    
    def view_cart(self, customer_id: int) -> Dict[str, Any]:
        """View customer's cart"""
        try:
            print(f"👀 Viewing cart for customer: {customer_id}")
            
            cart_items = self.db.execute_query("""
                SELECT c.*, p.name, p.price, p.description, p.stock_quantity 
                FROM cart c 
                JOIN products p ON c.product_id = p.id 
                WHERE c.customer_id = %s
                ORDER BY c.added_at DESC
            """, (customer_id,))
            
            if not cart_items:
                print("ℹ️ Cart is empty")
                return {"success": True, "items": [], "total": 0.0, "count": 0}
            
            items = []
            total = 0.0
            
            for item in cart_items:
                item_total = float(item['price']) * item['quantity']
                total += item_total
                
                items.append({
                    "product_id": item['product_id'],
                    "name": item['name'],
                    "price": float(item['price']),
                    "quantity": item['quantity'],
                    "subtotal": item_total,
                    "description": item['description'],
                    "stock_available": item['stock_quantity']
                })
            
            print(f"✅ Cart loaded: {len(items)} items, total: ${total:.2f}")
            return {
                "success": True,
                "items": items,
                "total": total,
                "count": len(items)
            }
            
        except Exception as e:
            print(f"❌ Error in view_cart: {e}")
            return {"success": False, "items": [], "total": 0.0, "count": 0}
    
    def remove_from_cart(self, customer_id: int, product_id: int) -> Dict[str, Any]:
        """Remove item from cart"""
        try:
            print(f"🗑️ Removing from cart: customer={customer_id}, product_id={product_id}")
            
            # Get product name first
            product = self.db.execute_query(
                "SELECT p.name FROM cart c JOIN products p ON c.product_id = p.id WHERE c.customer_id = %s AND c.product_id = %s",
                (customer_id, product_id)
            )
            
            if not product:
                return {"success": False, "message": "Item not found in cart"}
            
            product_name = product[0]['name']
            
            # Remove from cart
            self.db.execute_update(
                "DELETE FROM cart WHERE customer_id = %s AND product_id = %s",
                (customer_id, product_id)
            )
            
            print(f"✅ Removed from cart: {product_name}")
            return {"success": True, "message": f"Removed {product_name} from cart"}
            
        except Exception as e:
            print(f"❌ Error in remove_from_cart: {e}")
            return {"success": False, "message": "Error removing from cart"}
    
    def confirm_order(self, customer_id: int, delivery_address: str) -> Dict[str, Any]:
        """Confirm and place order"""
        try:
            print(f"📦 Confirming order: customer={customer_id}, address='{delivery_address}'")
            
            # Get cart items
            cart_items = self.db.execute_query("""
                SELECT c.*, p.name, p.price, p.stock_quantity 
                FROM cart c 
                JOIN products p ON c.product_id = p.id 
                WHERE c.customer_id = %s
            """, (customer_id,))
            
            if not cart_items:
                return {"success": False, "message": "Cart is empty"}
            
            # Calculate total and check stock
            total_amount = 0.0
            out_of_stock = []
            
            for item in cart_items:
                if item['stock_quantity'] < item['quantity']:
                    out_of_stock.append(f"{item['name']} (need {item['quantity']}, have {item['stock_quantity']})")
                total_amount += float(item['price']) * item['quantity']
            
            if out_of_stock:
                return {
                    "success": False, 
                    "message": f"Some items are out of stock: {', '.join(out_of_stock)}"
                }
            
            # Create order
            order_id = self.db.execute_update(
                "INSERT INTO orders (customer_id, total_amount, status, delivery_address, created_at) VALUES (%s, %s, %s, %s, %s)",
                (customer_id, total_amount, 'pending', delivery_address, datetime.now())
            )
            
            # Create order items and update stock
            for item in cart_items:
                # Add order item
                self.db.execute_update(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                    (order_id, item['product_id'], item['quantity'], item['price'])
                )
                
                # Update product stock
                self.db.execute_update(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s",
                    (item['quantity'], item['product_id'])
                )
            
            # Clear cart
            self.db.execute_update(
                "DELETE FROM cart WHERE customer_id = %s",
                (customer_id,)
            )
            
            print(f"✅ Order placed successfully: #{order_id}")
            return {
                "success": True,
                "message": f"Order #{order_id} placed successfully! Total: ${total_amount:.2f}",
                "order_id": order_id,
                "total": total_amount,
                "delivery_address": delivery_address,
                "item_count": len(cart_items)
            }
            
        except Exception as e:
            print(f"❌ Error in confirm_order: {e}")
            return {"success": False, "message": "Error placing order"}
    
    def check_order_status(self, customer_id: int) -> Dict[str, Any]:
        """Check customer's recent orders"""
        try:
            print(f"📋 Checking orders for customer: {customer_id}")
            
            orders = self.db.execute_query("""
                SELECT o.*, 
                       COUNT(oi.id) as item_count
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.customer_id = %s 
                GROUP BY o.id
                ORDER BY o.created_at DESC 
                LIMIT 5
            """, (customer_id,))
            
            if not orders:
                print("ℹ️ No orders found")
                return {"success": True, "orders": [], "message": "No orders found"}
            
            order_list = []
            for order in orders:
                order_list.append({
                    "order_id": order['id'],
                    "total": float(order['total_amount']),
                    "status": order['status'],
                    "created_at": order['created_at'].strftime("%Y-%m-%d %H:%M"),
                    "delivery_address": order['delivery_address'],
                    "item_count": order['item_count']
                })
            
            print(f"✅ Found {len(orders)} orders")
            return {"success": True, "orders": order_list}
            
        except Exception as e:
            print(f"❌ Error in check_order_status: {e}")
            return {"success": True, "orders": []}
    
    def save_conversation(self, customer_id: int, message: str, response: str):
        """Save conversation to history"""
        try:
            # Delete old conversations (keep only last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            self.db.execute_update(
                "DELETE FROM conversation_history WHERE customer_id = %s AND timestamp < %s",
                (customer_id, thirty_days_ago)
            )
            
            # Save new conversation
            self.db.execute_update(
                "INSERT INTO conversation_history (customer_id, message, response, timestamp) VALUES (%s, %s, %s, %s)",
                (customer_id, message, response, datetime.now())
            )
            print("💾 Conversation saved")
        except Exception as e:
            print(f"⚠️ Error saving conversation: {e}")
    
    def get_conversation_history(self, customer_id: int) -> List[Dict]:
        """Get recent conversation history"""
        try:
            conversations = self.db.execute_query("""
                SELECT * FROM conversation_history 
                WHERE customer_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (customer_id,))
            
            return [
                {
                    "message": conv['message'],
                    "response": conv['response'],
                    "timestamp": conv['timestamp']
                }
                for conv in reversed(conversations)
            ]
        except Exception as e:
            print(f"⚠️ Error getting conversation history: {e}")
            return []