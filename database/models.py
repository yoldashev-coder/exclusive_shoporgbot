import sqlite3
import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    '''Database manager for SQLite operations'''

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        '''Initialize database tables'''
        async with aiosqlite.connect(self.db_path) as db:
            # Users table - stores user registration data
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    language TEXT DEFAULT 'uz',
                    promo_used INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Cart table - stores shopping cart items
            await db.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    image TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Orders table - stores completed orders
            await db.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    discount_amount REAL DEFAULT 0,
                    final_amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Order items table - stores individual items in each order
            await db.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                )
            ''')

            await db.commit()

    # ============ USER OPERATIONS ============

    async def add_user(self, user_id: int, first_name: str, last_name: str,
                       email: str, phone: str, language: str = 'uz') -> bool:
        '''Register a new user'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO users (user_id, first_name, last_name, email, phone, language)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, first_name, last_name, email, phone, language))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        '''Get user by ID'''
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def user_exists(self, user_id: int) -> bool:
        '''Check if user is registered'''
        user = await self.get_user(user_id)
        return user is not None

    async def update_user_language(self, user_id: int, language: str) -> bool:
        '''Update user's language preference'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('UPDATE users SET language = ? WHERE user_id = ?',
                                (language, user_id))
                await db.commit()
                return True
        except:
            return False

    async def get_user_language(self, user_id: int) -> str:
        '''Get user's language preference'''
        user = await self.get_user(user_id)
        return user['language'] if user else 'uz'

    async def mark_promo_used(self, user_id: int) -> bool:
        '''Mark promo code as used for user'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('UPDATE users SET promo_used = 1 WHERE user_id = ?',
                                (user_id,))
                await db.commit()
                return True
        except:
            return False

    async def has_used_promo(self, user_id: int) -> bool:
        '''Check if user has used promo code'''
        user = await self.get_user(user_id)
        return user['promo_used'] == 1 if user else False

    async def get_all_users(self) -> List[int]:
        '''Get all user IDs for broadcasting'''
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT user_id FROM users') as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    # ============ CART OPERATIONS ============

    async def add_to_cart(self, user_id: int, product_id: int, title: str,
                          price: float, image: str = None) -> bool:
        '''Add product to cart or increase quantity'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if product already in cart
                async with db.execute('''
                    SELECT quantity FROM cart
                    WHERE user_id = ? AND product_id = ?
                ''', (user_id, product_id)) as cursor:
                    row = await cursor.fetchone()

                if row:
                    # Increase quantity if already exists
                    await db.execute('''
                        UPDATE cart SET quantity = quantity + 1
                        WHERE user_id = ? AND product_id = ?
                    ''', (user_id, product_id))
                else:
                    # Add new item to cart
                    await db.execute('''
                        INSERT INTO cart (user_id, product_id, title, price, image)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, product_id, title, price, image))

                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False

    async def get_cart(self, user_id: int) -> List[Dict[str, Any]]:
        '''Get user's cart items'''
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM cart WHERE user_id = ?
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        '''Remove product from cart'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    DELETE FROM cart WHERE user_id = ? AND product_id = ?
                ''', (user_id, product_id))
                await db.commit()
                return True
        except:
            return False

    async def clear_cart(self, user_id: int) -> bool:
        '''Clear all items from user's cart'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
                await db.commit()
                return True
        except:
            return False

    async def get_cart_total(self, user_id: int) -> float:
        '''Calculate total cart value'''
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT SUM(price * quantity) as total FROM cart WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row[0] else 0.0

    # ============ ORDER OPERATIONS ============

    async def create_order(self, user_id: int, total_amount: float,
                          discount_amount: float, final_amount: float,
                          payment_method: str, latitude: float = None,
                          longitude: float = None) -> Optional[int]:
        '''Create a new order and return order ID'''
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    INSERT INTO orders (user_id, total_amount, discount_amount,
                                      final_amount, payment_method, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, total_amount, discount_amount, final_amount,
                     payment_method, latitude, longitude))

                order_id = cursor.lastrowid

                # Add cart items to order_items
                cart_items = await self.get_cart(user_id)
                for item in cart_items:
                    await db.execute('''
                        INSERT INTO order_items (order_id, product_id, title, price, quantity)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (order_id, item['product_id'], item['title'],
                         item['price'], item['quantity']))

                await db.commit()
                return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    async def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
        '''Get all orders for a user'''
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_total_orders_count(self) -> int:
        '''Get total number of orders (for admin)'''
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT COUNT(*) FROM orders') as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0