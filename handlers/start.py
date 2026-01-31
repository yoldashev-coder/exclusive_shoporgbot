from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.models import Database
from keyboards.reply import get_language_keyboard, get_main_menu_keyboard
from keyboards.inline import get_categories_keyboard
from utils.translations import get_text
from config import LANGUAGES, DATABASE_PATH, ADMIN_IDS
from states.user_states import RegistrationStates

router = Router()
db = Database(DATABASE_PATH)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    '''Handle /start command - language selection or main menu'''
    await state.clear()
    user_id = message.from_user.id

    # Check if user is registered
    if await db.user_exists(user_id):
        # User is registered, show main menu
        lang = await db.get_user_language(user_id)
        user = await db.get_user(user_id)
        is_admin = user_id in ADMIN_IDS

        await message.answer(
            get_text('main_menu', lang),
            reply_markup=get_main_menu_keyboard(lang, is_admin)
        )
    else:
        # New user, show language selection
        await message.answer(
            get_text('select_language', 'uz'),
            reply_markup=get_language_keyboard()
        )

@router.message(F.text.in_([LANGUAGES[lang] for lang in LANGUAGES]))
async def language_selected(message: Message, state: FSMContext):
    '''Handle language selection'''
    # Determine selected language
    selected_lang = None
    for code, name in LANGUAGES.items():
        if message.text == name:
            selected_lang = code
            break

    if not selected_lang:
        return

    await state.update_data(language=selected_lang)

    # Check if user is registered
    user_id = message.from_user.id
    if await db.user_exists(user_id):
        # Update language for existing user
        await db.update_user_language(user_id, selected_lang)
        user = await db.get_user(user_id)
        is_admin = user_id in ADMIN_IDS

        await message.answer(
            get_text('language_changed', selected_lang),
            reply_markup=get_main_menu_keyboard(selected_lang, is_admin)
        )
    else:
        # New user, start registration
        await message.answer(
            get_text('welcome_register', selected_lang)
        )
        await message.answer(
            get_text('enter_first_name', selected_lang)
        )
        await state.set_state(RegistrationStates.waiting_for_first_name)

@router.message(F.text == get_text('settings', 'uz'))
@router.message(F.text == get_text('settings', 'ru'))
@router.message(F.text == get_text('settings', 'en'))
async def settings_menu(message: Message):
    '''Handle settings button - allow language change'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    await message.answer(
        get_text('select_language', lang),
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery):
    '''Handle back to main menu callback'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)
    is_admin = user_id in ADMIN_IDS

    await callback.message.edit_text(
        get_text('main_menu', lang)
    )
    await callback.message.answer(
        get_text('main_menu', lang),
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )
    await callback.answer()