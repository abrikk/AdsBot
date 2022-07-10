from aiogram import Dispatcher
from aiogram_dialog import DialogRegistry

from tgbot.handlers.buy_and_sell.buy_and_sell_dialogs import sell_dialog, buy_dialog
from tgbot.handlers.main_handler import main_dialog
from tgbot.handlers.start import register_start
from tgbot.handlers.test import register_test


def register_all_dialogs(dialog_registry: DialogRegistry):
    dialog_registry.register(main_dialog)
    dialog_registry.register(sell_dialog)
    dialog_registry.register(buy_dialog)


def register_all_handlers(dp: Dispatcher):
    register_start(dp)
    register_test(dp)
