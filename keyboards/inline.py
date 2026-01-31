from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.translations import get_text
from typing import List, Dict, Any

def get_categories_keyboard(categories: List[Dict[str, Any]], lang: str = 'uz') -> InlineKeyboardMarkup:
    '''Create inline keyboard for categories'''
    builder = InlineKeyboardBuilder()

    # Add "All Products" button
    builder.button(
        text=get_text('all_products', lang),
        callback_data='category_all'
    )

    # Add category buttons
    for category in categories:
        if not isinstance(category, dict):
            continue
            
        name = str(category.get('name', 'Category'))
        slug = str(category.get('slug', ''))
        
        if not slug:
            continue
            
        builder.button(
            text=f"📂 {name}",
            callback_data=f"category_{slug}"
        )

    builder.button(
        text=get_text('back', lang),
        callback_data='back_to_menu'
    )

    builder.adjust(2)
    return builder.as_markup()

def get_product_keyboard(product_id: int, lang: str = 'uz',
                         show_pagination: bool = False,
                         current_page: int = 0,
                         total_pages: int = 0) -> InlineKeyboardMarkup:
    '''Create inline keyboard for product card'''
    builder = InlineKeyboardBuilder()

    # Add to cart button
    builder.button(
        text=get_text('add_to_cart', lang),
        callback_data=f'add_to_cart_{product_id}'
    )

    # Pagination buttons if needed
    if show_pagination and total_pages > 1:
        buttons_row = []

        if current_page > 0:
            buttons_row.append(InlineKeyboardButton(
                text=get_text('previous', lang),
                callback_data=f'page_{current_page - 1}'
            ))

        buttons_row.append(InlineKeyboardButton(
            text=f'{current_page + 1}/{total_pages}',
            callback_data='current_page'
        ))

        if current_page < total_pages - 1:
            buttons_row.append(InlineKeyboardButton(
                text=get_text('next', lang),
                callback_data=f'page_{current_page + 1}'
            ))

        builder.row(*buttons_row)

    # Back button
    builder.button(
        text=get_text('back', lang),
        callback_data='back_to_categories'
    )

    builder.adjust(1)
    return builder.as_markup()

def get_cart_keyboard(cart_items: List[Dict[str, Any]], lang: str = 'uz') -> InlineKeyboardMarkup:
    '''Create inline keyboard for cart'''
    builder = InlineKeyboardBuilder()

    if cart_items:
        # Remove buttons for each item
        for item in cart_items:
            builder.button(
                text=f"🗑 {item['title']} (x{item['quantity']})",
                callback_data=f"remove_from_cart_{item['product_id']}"
            )

        # Clear cart and checkout buttons
        builder.button(
            text=get_text('clear_cart', lang),
            callback_data='clear_cart'
        )
        builder.button(
            text=get_text('checkout', lang),
            callback_data='checkout'
        )

    builder.button(
        text=get_text('back', lang),
        callback_data='back_to_menu'
    )

    builder.adjust(1)
    return builder.as_markup()

def get_admin_keyboard(lang: str = 'uz') -> InlineKeyboardMarkup:
    '''Create admin panel keyboard'''
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_text('total_orders', lang),
        callback_data='admin_orders'
    )
    builder.button(
        text=get_text('broadcast', lang),
        callback_data='admin_broadcast'
    )
    builder.button(
        text=get_text('back', lang),
        callback_data='back_to_menu'
    )

    builder.adjust(1)
    return builder.as_markup()