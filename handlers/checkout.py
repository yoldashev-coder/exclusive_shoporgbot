from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.models import Database
from keyboards.reply import get_location_keyboard, get_payment_keyboard, get_promo_keyboard, get_main_menu_keyboard
from utils.translations import get_text
from states.user_states import CheckoutStates
from config import DATABASE_PATH, PROMO_CODE, PROMO_DISCOUNT, ADMIN_IDS

router = Router()
db = Database(DATABASE_PATH)

@router.callback_query(F.data == 'checkout')
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    '''Start checkout process'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    # Check if cart is empty
    cart_items = await db.get_cart(user_id)
    if not cart_items:
        await callback.answer(get_text('cart_empty', lang), show_alert=True)
        return

    # Calculate total
    total = await db.get_cart_total(user_id)
    await state.update_data(total_amount=total)

    # Ask for promo code
    await callback.message.answer(
        get_text('enter_promo', lang),
        reply_markup=get_promo_keyboard(lang)
    )
    await state.set_state(CheckoutStates.waiting_for_promo)
    await callback.answer()

@router.message(CheckoutStates.waiting_for_promo)
async def process_promo(message: Message, state: FSMContext):
    '''Process promo code input'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    data = await state.get_data()
    total_amount = data.get('total_amount', 0)
    discount_amount = 0

    promo_text = message.text.strip().upper()

    # Check if user skipped promo
    if message.text == get_text('skip', lang):
        final_amount = total_amount
    elif promo_text == PROMO_CODE:
        # Check if user already used promo
        has_used = await db.has_used_promo(user_id)
        if has_used:
            await message.answer(get_text('promo_used', lang))
            final_amount = total_amount
        else:
            # Apply promo discount
            discount_amount = total_amount * (PROMO_DISCOUNT / 100)
            final_amount = total_amount - discount_amount
            await message.answer(
                get_text('promo_applied', lang, percent=PROMO_DISCOUNT)
            )
            await db.mark_promo_used(user_id)
    else:
        # Invalid promo code
        await message.answer(get_text('promo_invalid', lang))
        final_amount = total_amount

    # Save amounts to state
    await state.update_data(
        discount_amount=discount_amount,
        final_amount=final_amount
    )

    # Ask for location
    await message.answer(
        get_text('send_location', lang),
        reply_markup=get_location_keyboard(lang)
    )
    await state.set_state(CheckoutStates.waiting_for_location)

@router.message(CheckoutStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    '''Process delivery location'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    latitude = message.location.latitude
    longitude = message.location.longitude

    await state.update_data(
        latitude=latitude,
        longitude=longitude
    )

    # Ask for payment method
    await message.answer(
        get_text('select_payment', lang),
        reply_markup=get_payment_keyboard(lang)
    )
    await state.set_state(CheckoutStates.waiting_for_payment)

@router.message(CheckoutStates.waiting_for_payment)
async def process_payment(message: Message, state: FSMContext):
    '''Process payment method and complete order'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    payment_text = message.text

    # Validate payment method
    if payment_text not in [get_text('cash', lang), get_text('card', lang)]:
        await message.answer(get_text('select_payment', lang))
        return

    # Get all checkout data
    data = await state.get_data()
    total_amount = data.get('total_amount', 0)
    discount_amount = data.get('discount_amount', 0)
    final_amount = data.get('final_amount', 0)
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    payment_method = 'cash' if payment_text == get_text('cash', lang) else 'card'

    # Create order in database
    order_id = await db.create_order(
        user_id=user_id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        payment_method=payment_method,
        latitude=latitude,
        longitude=longitude
    )

    if order_id:
        # Clear cart after successful order
        await db.clear_cart(user_id)

        # Send confirmation
        is_admin = user_id in ADMIN_IDS
        success_text = get_text('order_success', lang)
        success_text += f"\n\n{get_text('order_number', lang)}: #{order_id}"
        success_text += f"\n💵 {get_text('total', lang)}: ${final_amount:.2f}"

        await message.answer(
            success_text,
            reply_markup=get_main_menu_keyboard(lang, is_admin)
        )
        await state.clear()
    else:
        await message.answer("❌ Order failed. Please try again.")
        await state.clear()