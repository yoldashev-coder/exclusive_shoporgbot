from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from database.models import Database
from services.api_service import DummyJSONService
from keyboards.inline import get_categories_keyboard, get_product_keyboard
from utils.translations import get_text
from config import DATABASE_PATH

router = Router()
db = Database(DATABASE_PATH)
api = DummyJSONService()

# Store current browsing state per user
user_browse_state = {}

@router.message(F.text.in_([get_text('catalog', 'uz'), get_text('catalog', 'ru'), get_text('catalog', 'en')]))
async def show_catalog(message: Message):
    '''Show product catalog with categories'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    loading_msg = await message.answer(get_text('loading', lang))

    # Fetch categories from API
    categories = await api.get_categories()

    await loading_msg.delete()

    await message.answer(
        get_text('categories', lang),
        reply_markup=get_categories_keyboard(categories, lang)
    )

@router.callback_query(F.data.startswith('category_'))
async def show_category_products(callback: CallbackQuery):
    '''Show products from selected category'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    category = callback.data.replace('category_', '')

    await callback.message.edit_text(get_text('loading', lang))

    # Fetch products
    if category == 'all':
        result = await api.get_products(limit=30)
        products = result.get('products', [])
    else:
        products = await api.get_products_by_category(category, limit=30)

    if not products:
        await callback.message.edit_text(get_text('no_results', lang))
        await callback.answer()
        return

    # Store products in user state for pagination
    user_browse_state[user_id] = {
        'products': products,
        'current_page': 0
    }

    # Show first product
    await show_product_page(callback.message, user_id, 0, edit=True)
    await callback.answer()

async def show_product_page(message: Message, user_id: int, page: int, edit: bool = False):
    '''Display a single product page'''
    lang = await db.get_user_language(user_id)

    if user_id not in user_browse_state:
        return

    products = user_browse_state[user_id]['products']

    if page < 0 or page >= len(products):
        return

    product = products[page]
    user_browse_state[user_id]['current_page'] = page

    # Format product information
    text = api.format_product_text(product, lang)

    # Get product image
    image_url = product.get('thumbnail') or product.get('images', [''])[0]

    # Create keyboard
    keyboard = get_product_keyboard(
        product_id=product['id'],
        lang=lang,
        show_pagination=True,
        current_page=page,
        total_pages=len(products)
    )

    try:
        if edit:
            # Try to edit with new media
            try:
                await message.edit_media(
                    media=InputMediaPhoto(media=image_url, caption=text, parse_mode='HTML'),
                    reply_markup=keyboard
                )
            except:
                # If edit fails, delete and send new
                await message.delete()
                await message.answer_photo(
                    photo=image_url,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        else:
            await message.answer_photo(
                photo=image_url,
                caption=text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
    except Exception as e:
        # Fallback to text if image fails
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML')

@router.callback_query(F.data.startswith('page_'))
async def navigate_products(callback: CallbackQuery):
    '''Handle product pagination'''
    user_id = callback.from_user.id
    page = int(callback.data.replace('page_', ''))

    await show_product_page(callback.message, user_id, page, edit=True)
    await callback.answer()

@router.callback_query(F.data == 'back_to_categories')
async def back_to_categories(callback: CallbackQuery):
    '''Return to categories menu'''
    user_id = callback.from_user.id
    lang = await db.get_user_language(user_id)

    # Clear user browse state
    if user_id in user_browse_state:
        del user_browse_state[user_id]

    categories = await api.get_categories()

    await callback.message.delete()
    await callback.message.answer(
        get_text('categories', lang),
        reply_markup=get_categories_keyboard(categories, lang)
    )
    await callback.answer()