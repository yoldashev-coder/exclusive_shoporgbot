from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database.models import Database
from keyboards.inline import get_admin_keyboard
from keyboards.reply import get_main_menu_keyboard
from utils.translations import get_text
from states.user_states import BroadcastStates
from config import DATABASE_PATH, ADMIN_IDS

router = Router()
db = Database(DATABASE_PATH)

def is_admin(user_id: int) -> bool:
    '''Check if user is admin'''
    return user_id in ADMIN_IDS

@router.message(F.text.in_([get_text('admin_panel', 'uz'), get_text('admin_panel', 'ru'), get_text('admin_panel', 'en')]))
async def admin_panel(message: Message):
    '''Show admin panel'''
    user_id = message.from_user.id

    if not is_admin(user_id):
        return

    lang = await db.get_user_language(user_id)

    await message.answer(
        f"👨‍💼 <b>{get_text('admin_panel', lang)}</b>",
        reply_markup=get_admin_keyboard(lang),
        parse_mode='HTML'
    )

@router.callback_query(F.data == 'admin_orders')
async def show_total_orders(callback: CallbackQuery):
    '''Show total orders statistics'''
    user_id = callback.from_user.id

    if not is_admin(user_id):
        await callback.answer("❌ Access denied", show_alert=True)
        return

    lang = await db.get_user_language(user_id)

    # Get total orders count
    total_orders = await db.get_total_orders_count()

    text = f"📊 <b>{get_text('total_orders', lang)}</b>\n\n"
    text += f"Jami buyurtmalar soni: <b>{total_orders}</b>"

    await callback.message.edit_text(
        text,
        reply_markup=get_admin_keyboard(lang),
        parse_mode='HTML'
    )
    await callback.answer()

@router.callback_query(F.data == 'admin_broadcast')
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    '''Start broadcast message flow'''
    user_id = callback.from_user.id

    if not is_admin(user_id):
        await callback.answer("❌ Access denied", show_alert=True)
        return

    lang = await db.get_user_language(user_id)

    await callback.message.answer(get_text('enter_broadcast', lang))
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.answer()

@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext):
    '''Send broadcast message to all users'''
    user_id = message.from_user.id

    if not is_admin(user_id):
        return

    lang = await db.get_user_language(user_id)

    # Get all users
    all_users = await db.get_all_users()

    # Send message to all users
    success_count = 0
    for target_user_id in all_users:
        try:
            await message.copy_to(target_user_id)
            success_count += 1
        except:
            pass  # User blocked the bot or other error

    # Send confirmation
    await message.answer(
        get_text('broadcast_success', lang, count=success_count),
        reply_markup=get_main_menu_keyboard(lang, is_admin=True)
    )
    await state.clear()