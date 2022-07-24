from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

conf_cb = CallbackData("approve", "post_id", "action")


def confirm_post(post_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Да",
            callback_data=conf_cb.new(post_id=str(post_id), action="yes")
        ),
        InlineKeyboardButton(
            text="Нет",
            callback_data=conf_cb.new(post_id=str(post_id), action="no")
        )
    )
    return markup


def show_posted_ad(post_link: str):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Посмотреть объявление 📢",
            url=post_link
        )
    )
    return markup


def join_link(bot_link: str, channel_link: str):
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton(
            text="Перейти к боту 🤖",
            url=bot_link
        ),
        InlineKeyboardButton(
            text="Перейти в канал 📢",
            url=channel_link
        )
    )
    return markup


manage_cb = CallbackData("manage", "post_id", "action")


def manage_post(post_id: int):
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton(
            text="Удалить объявление ❌",
            callback_data=manage_cb.new(post_id=str(post_id), action="bot")
        ),
        InlineKeyboardButton(
            text="Управление пользователем ⚙️️",
            url=manage_cb.new(post_id=str(post_id), action="channel")
        )
    )
    return markup
