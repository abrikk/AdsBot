from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

conf_cb = CallbackData("approve", "post_id", "status")


def confirm_post(post_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Да",
            callback_data=conf_cb.new(post_id=str(post_id), status="active")
        ),
        InlineKeyboardButton(
            text="Нет",
            callback_data=conf_cb.new(post_id=str(post_id), status="inactive")
        )
    )
    return markup
