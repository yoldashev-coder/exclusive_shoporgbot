from aiogram import Router, F
from aiogram.types import Message
from database.models import Database
from utils.translations import get_text
from config import DATABASE_PATH

router = Router()
db = Database(DATABASE_PATH)

@router.message(F.text.in_([get_text('my_orders', 'uz'), get_text('my_orders', 'ru'), get_text('my_orders', 'en')]))
async def show_my_orders(message: Message):
    '''Show user's order history'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    # Get user orders
    orders = await db.get_user_orders(user_id)

    if not orders:
        await message.answer(f"📦 {get_text('my_orders', lang)}\n\nSizda hali buyurtmalar yo'q.")
        return

    # Format orders message
    text = f"📦 <b>{get_text('my_orders', lang)}</b>\n\n"

    for order in orders[:10]:  # Show last 10 orders
        status_emoji = "✅" if order['status'] == 'completed' else "⏳"
        text += f"{status_emoji} <b>Buyurtma #{order['id']}</b>\n"
        text += f"💰 Summa: ${order['final_amount']:.2f}\n"
        text += f"💳 To'lov: {order['payment_method']}\n"
        text += f"📅 Sana: {order['created_at'][:10]}\n\n"

    await message.answer(text, parse_mode='HTML')