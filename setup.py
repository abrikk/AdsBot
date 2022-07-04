from aiogram import Dispatcher
from aiogram_dialog import DialogRegistry

from tgbot.handlers.test import register_test


def register_all_dialogs(dialog_registry: DialogRegistry):
    pass


def register_all_handlers(dp: Dispatcher):
    register_test(dp)
