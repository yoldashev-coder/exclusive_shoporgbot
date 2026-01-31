import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Database configuration
DATABASE_PATH = 'shop_database.db'

# API configuration
DUMMYJSON_API_URL = 'https://dummyjson.com'

# Promo code configuration
PROMO_CODE = 'HELLO'
PROMO_DISCOUNT = 10  # Percentage

# Supported languages
LANGUAGES = {
    'uz': '🇺🇿 O\'zbekcha',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}