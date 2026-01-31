from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.translations import get_text
from config import LANGUAGES

def get_language_keyboard() -> ReplyKeyboardMarkup:
    '''Create language selection keyboard'''
    builder = ReplyKeyboardBuilder()
    for code, name in LANGUAGES.items():
        builder.button(text=name)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_contact_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    '''Create contact sharing keyboard'''
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=get_text('share_contact_btn', lang),
        request_contact=True
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_main_menu_keyboard(lang: str = 'uz', is_admin: bool = False) -> ReplyKeyboardMarkup:
    '''Create main menu keyboard'''
    builder = ReplyKeyboardBuilder()

    builder.button(text=get_text('catalog', lang))
    builder.button(text=get_text('cart', lang))
    builder.button(text=get_text('search', lang))
    builder.button(text=get_text('my_orders', lang))
    builder.button(text=get_text('settings', lang))

    if is_admin:
        builder.button(text=get_text('admin_panel', lang))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_location_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    '''Create location sharing keyboard'''
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=get_text('send_location_btn', lang),
        request_location=True
    )
    builder.button(text=get_text('back', lang))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_payment_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    '''Create payment method selection keyboard'''
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_text('cash', lang))
    builder.button(text=get_text('card', lang))
    builder.button(text=get_text('back', lang))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_promo_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    '''Create promo code keyboard with skip option'''
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_text('skip', lang))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)