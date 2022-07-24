from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram_dialog import DialogManager


async def cancel(message: types.Message, dialog_manager: DialogManager):
    while dialog_manager.current_context():
        await dialog_manager.done()
    else:
        await message.answer("Чтобы то ни было - отменено.")


def register_cancel(dp: Dispatcher):
    dp.register_message_handler(cancel, Command("cancel"))
