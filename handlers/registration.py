from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.models import Database
from keyboards.reply import get_contact_keyboard, get_main_menu_keyboard
from utils.translations import get_text
from states.user_states import RegistrationStates
from config import DATABASE_PATH, ADMIN_IDS
import re

router = Router()
db = Database(DATABASE_PATH)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@router.message(RegistrationStates.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    '''Process first name input'''
    await state.update_data(first_name=message.text)
    data = await state.get_data()
    lang = data.get('language', 'uz')

    await message.answer(get_text('enter_last_name', lang))
    await state.set_state(RegistrationStates.waiting_for_last_name)

@router.message(RegistrationStates.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    '''Process last name input'''
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    lang = data.get('language', 'uz')

    await message.answer(get_text('enter_email', lang))
    await state.set_state(RegistrationStates.waiting_for_email)

@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    '''Process email input with validation'''
    email = message.text.strip()
    data = await state.get_data()
    lang = data.get('language', 'uz')

    # Validate email format
    if not EMAIL_REGEX.match(email):
        await message.answer(get_text('invalid_email', lang))
        return

    await state.update_data(email=email)

    await message.answer(
        get_text('share_contact', lang),
        reply_markup=get_contact_keyboard(lang)
    )
    await state.set_state(RegistrationStates.waiting_for_phone)

@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    '''Process phone number via contact sharing'''
    phone = message.contact.phone_number
    user_id = message.from_user.id

    # Get all registration data
    data = await state.get_data()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    lang = data.get('language', 'uz')

    # Save user to database
    success = await db.add_user(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        language=lang
    )

    if success:
        is_admin = user_id in ADMIN_IDS
        await message.answer(
            get_text('registration_complete', lang),
            reply_markup=get_main_menu_keyboard(lang, is_admin)
        )
        await state.clear()
    else:
        await message.answer("❌ Registration failed. Please try again with /start")
        await state.clear()