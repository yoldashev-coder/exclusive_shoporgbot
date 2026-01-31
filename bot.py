import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, DATABASE_PATH
from database.models import Database

# Import handlers
from handlers import start, registration, catalog, cart, checkout, search, admin, orders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    '''Main bot entry point'''

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Initialize database
    db = Database(DATABASE_PATH)
    await db.init_db()
    logger.info("Database initialized successfully")

    # Register routers
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(checkout.router)
    dp.include_router(search.router)
    dp.include_router(admin.router)
    dp.include_router(orders.router)

    logger.info("All handlers registered")

    # Start polling
    try:
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")