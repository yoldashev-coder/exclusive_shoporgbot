from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from database.models import Database
from services.api_service import DummyJSONService
from keyboards.inline import get_product_keyboard
from keyboards.reply import get_main_menu_keyboard
from utils.translations import get_text
from states.user_states import SearchStates
from config import DATABASE_PATH, ADMIN_IDS

router = Router()
db = Database(DATABASE_PATH)
api = DummyJSONService()

# Store search results per user
user_search_results = {}

@router.message(F.text.in_([get_text('search', 'uz'), get_text('search', 'ru'), get_text('search', 'en')]))
async def start_search(message: Message, state: FSMContext):
    '''Start product search flow'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)

    await message.answer(get_text('enter_search', lang))
    await state.set_state(SearchStates.waiting_for_query)

@router.message(SearchStates.waiting_for_query)
async def process_search(message: Message, state: FSMContext):
    '''Process search query and show results'''
    user_id = message.from_user.id
    lang = await db.get_user_language(user_id)
    query = message.text.strip()

    loading_msg = await message.answer(get_text('loading', lang))

    # Search products via API
    products = await api.search_products(query)

    await loading_msg.delete()

    if not products:
        is_admin = user_id in ADMIN_IDS
        await message.answer(
            get_text('no_results', lang),
            reply_markup=get_main_menu_keyboard(lang, is_admin)
        )
        await state.clear()
        return

    # Store search results
    user_search_results[user_id] = {
        'products': products,
        'current_page': 0
    }

    # Show first result
    await show_search_result(message, user_id, 0)
    await state.clear()

async def show_search_result(message: Message, user_id: int, page: int, edit: bool = False):
    '''Display a single search result'''
    lang = await db.get_user_language(user_id)

    if user_id not in user_search_results:
        return

    products = user_search_results[user_id]['products']

    if page < 0 or page >= len(products):
        return

    product = products[page]
    user_search_results[user_id]['current_page'] = page

    # Format product information
    text = f"🔍 <b>{get_text('search_results', lang)}</b>\n\n"
    text += api.format_product_text(product, lang)

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
            try:
                await message.edit_media(
                    media=InputMediaPhoto(media=image_url, caption=text, parse_mode='HTML'),
                    reply_markup=keyboard
                )
            except:
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
    except:
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML')

@router.callback_query(F.data.startswith('search_page_'))
async def navigate_search_results(callback: CallbackQuery):
    '''Navigate through search results'''
    user_id = callback.from_user.id
    page = int(callback.data.replace('search_page_', ''))

    await show_search_result(callback.message, user_id, page, edit=True)
    await callback.answer()