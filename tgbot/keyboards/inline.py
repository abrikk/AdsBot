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
        # InlineKeyboardButton(
        #     text="Перейти в канал 📢",
        #     url=channel_link
        # )
    )
    return markup


manage_cb = CallbackData("manage", "post_id", "user_id", "full_name")


def manage_post(user_id: int | str, full_name: str = None, post_id: int | str = None, url: str = None, argument: str = None):
    markup = InlineKeyboardMarkup(row_width=1)

    if url:
        markup.add(
            InlineKeyboardButton(
                text="Перейти к объявлению 📢",
                url=url
            )
        )

    if argument != "only_search_user":
        markup.add(
            InlineKeyboardButton(
                text="Удалить объявление ❌",
                callback_data=manage_cb.new(post_id=str(post_id), user_id=str(user_id), full_name=full_name)
            )
        )
    markup.add(
        InlineKeyboardButton(
            text="Управление пользователем ⚙️️",
            switch_inline_query_current_chat=f"управление пользователем {full_name or user_id}: {user_id}"
        )
    )
    return markup


confirm_cb = CallbackData("confirm", "post_id", "user_id", "full_name", "action")


def confirm_delete_ad(post_id: str, user_id: str, full_name: str):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Да ✅",
            callback_data=confirm_cb.new(post_id=post_id, user_id=user_id, full_name=full_name, action="yes")
        ),
        InlineKeyboardButton(
            text="Нет ❌",
            callback_data=confirm_cb.new(post_id=post_id, user_id=user_id, full_name=full_name, action="no")
        )
    )
    return markup
