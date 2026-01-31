from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.models import Database
from services.api_service import DummyJSONService
from keyboards.inline import get_cart_keyboard
from utils.translations import get_text
from config import DATABASE_PATH

router = Router()
db = Database(DATABASE_PATH)
api = DummyJSONService()

@router.callback_query(F.data.startswith('add_to_cart_'))
async def add_to_cart(callback: CallbackQuery):
    '''Add product to shopping cart'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    product_id = int(callback.data.replace('add_to_cart_', ''))

    # Fetch product details from API
    product = await api.get_product_by_id(product_id)

    if not product:
        await callback.answer("❌ Product not found", show_alert=True)
        return

    # Calculate final price with discount
    price = product.get('price', 0)
    discount = product.get('discountPercentage', 0)
    final_price = price - (price * discount / 100)

    # Add to cart in database
    success = await db.add_to_cart(
        user_id=user_id,
        product_id=product_id,
        title=product.get('title', 'Product'),
        price=final_price,
        image=product.get('thumbnail')
    )

    if success:
        await callback.answer(get_text('added_to_cart', lang), show_alert=True)
    else:
        await callback.answer("❌ Failed to add to cart", show_alert=True)

@router.message(F.text.in_([get_text('cart', 'uz'), get_text('cart', 'ru'), get_text('cart', 'en')]))
async def show_cart(message: Message):
    '''Display shopping cart'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    # Get cart items
    cart_items = await db.get_cart(user_id)

    if not cart_items:
        await message.answer(
            get_text('cart_empty', lang),
            reply_markup=get_cart_keyboard([], lang)
        )
        return

    # Format cart message
    cart_text = f"🛒 <b>{get_text('your_cart', lang)}</b>\n\n"

    total = 0
    for item in cart_items:
        item_total = item['price'] * item['quantity']
        total += item_total
        cart_text += f"• <b>{item['title']}</b>\n"
        cart_text += f"  {get_text('quantity', lang)}: {item['quantity']}\n"
        cart_text += f"  {get_text('price', lang)}: ${item['price']:.2f} x {item['quantity']} = ${item_total:.2f}\n\n"

    cart_text += f"\n💵 <b>{get_text('total', lang)}: ${total:.2f}</b>"

    await message.answer(
        cart_text,
        reply_markup=get_cart_keyboard(cart_items, lang),
        parse_mode='HTML'
    )

@router.callback_query(F.data.startswith('remove_from_cart_'))
async def remove_from_cart(callback: CallbackQuery):
    '''Remove product from cart'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    product_id = int(callback.data.replace('remove_from_cart_', ''))

    success = await db.remove_from_cart(user_id, product_id)

    if success:
        # Refresh cart display
        cart_items = await db.get_cart(user_id)

        if not cart_items:
            await callback.message.edit_text(
                get_text('cart_empty', lang),
                reply_markup=get_cart_keyboard([], lang)
            )
        else:
            # Reformat cart
            cart_text = f"🛒 <b>{get_text('your_cart', lang)}</b>\n\n"
            total = 0
            for item in cart_items:
                item_total = item['price'] * item['quantity']
                total += item_total
                cart_text += f"• <b>{item['title']}</b>\n"
                cart_text += f"  {get_text('quantity', lang)}: {item['quantity']}\n"
                cart_text += f"  {get_text('price', lang)}: ${item['price']:.2f} x {item['quantity']} = ${item_total:.2f}\n\n"

            cart_text += f"\n💵 <b>{get_text('total', lang)}: ${total:.2f}</b>"

            await callback.message.edit_text(
                cart_text,
                reply_markup=get_cart_keyboard(cart_items, lang),
                parse_mode='HTML'
            )

        await callback.answer(get_text('removed_from_cart', lang))
    else:
        await callback.answer("❌ Failed to remove", show_alert=True)

@router.callback_query(F.data == 'clear_cart')
async def clear_cart(callback: CallbackQuery):
    '''Clear entire shopping cart'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    await db.clear_cart(user_id)

    await callback.message.edit_text(
        get_text('cart_empty', lang),
        reply_markup=get_cart_keyboard([], lang)
    )
    await callback.answer(get_text('removed_from_cart', lang))