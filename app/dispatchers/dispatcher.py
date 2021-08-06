from aiogram import Dispatcher
from .channel import channel_handler


def register_dispatcher(dispatcher: Dispatcher):
    dispatcher.register_my_chat_member_handler(channel_handler)
