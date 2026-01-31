from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    '''FSM states for user registration process'''
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()

class CheckoutStates(StatesGroup):
    '''FSM states for checkout process'''
    waiting_for_promo = State()
    waiting_for_location = State()
    waiting_for_payment = State()

class SearchStates(StatesGroup):
    '''FSM states for product search'''
    waiting_for_query = State()

class BroadcastStates(StatesGroup):
    '''FSM states for admin broadcast'''
    waiting_for_message = State()