import aiohttp
from typing import List, Dict, Any, Optional
from config import DUMMYJSON_API_URL

class DummyJSONService:
    '''Service for interacting with DummyJSON API'''

    def __init__(self):
        self.base_url = "https://dummyjson.com"

    async def get_categories(self) -> List[Dict[str, Any]]:
        '''Fetch all product categories'''
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.base_url}/products/categories') as response:
                    if response.status == 200:
                        categories = await response.json()
                        return categories
            return []
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    async def get_products(self, limit: int = 10, skip: int = 0) -> Dict[str, Any]:
        '''Fetch products with pagination'''
        try:
            async with aiohttp.ClientSession() as session:
                url = f'{self.base_url}/products?limit={limit}&skip={skip}'
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
            return {'products': [], 'total': 0}
        except Exception as e:
            print(f"Error fetching products: {e}")
            return {'products': [], 'total': 0}

    async def get_products_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        '''Fetch products by category'''
        try:
            async with aiohttp.ClientSession() as session:
                url = f'{self.base_url}/products/category/{category}?limit={limit}'
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('products', [])
            return []
        except Exception as e:
            print(f"Error fetching category products: {e}")
            return []

    async def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        '''Fetch single product by ID'''
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.base_url}/products/{product_id}') as response:
                    if response.status == 200:
                        product = await response.json()
                        return product
            return None
        except Exception as e:
            print(f"Error fetching product: {e}")
            return None

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        '''Search products by query'''
        try:
            async with aiohttp.ClientSession() as session:
                url = f'{self.base_url}/products/search?q={query}'
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('products', [])
            return []
        except Exception as e:
            print(f"Error searching products: {e}")
            return []

    @staticmethod
    def format_product_text(product: Dict[str, Any], lang: str = 'uz') -> str:
        '''Format product information for display'''
        title = product.get('title', 'N/A')
        description = product.get('description', 'No description')
        price = product.get('price', 0)
        discount = product.get('discountPercentage', 0)
        rating = product.get('rating', 0)

        # Calculate final price after discount
        final_price = price - (price * discount / 100)

        # Format rating with stars
        stars = '⭐' * int(rating)

        # Translate labels based on language
        labels = {
            'uz': {
                'desc': '📝 Tavsif',
                'price': '💰 Narx',
                'discount': '🎁 Chegirma',
                'final': '✨ Yakuniy narx',
                'rating': '⭐ Reyting'
            },
            'ru': {
                'desc': '📝 Описание',
                'price': '💰 Цена',
                'discount': '🎁 Скидка',
                'final': '✨ Итоговая цена',
                'rating': '⭐ Рейтинг'
            },
            'en': {
                'desc': '📝 Description',
                'price': '💰 Price',
                'discount': '🎁 Discount',
                'final': '✨ Final Price',
                'rating': '⭐ Rating'
            }
        }

        l = labels.get(lang, labels['en'])

        text = f"🛍 <b>{title}</b>\n\n"
        text += f"{l['desc']}: {description}\n\n"
        text += f"{l['price']}: ${price}\n"
        text += f"{l['discount']}: {discount}%\n"
        text += f"{l['final']}: <b>${final_price:.2f}</b>\n\n"
        text += f"{l['rating']}: {stars} ({rating}/5)\n"

        return text