from typing import Dict

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, Start, SwitchTo, Column, Back, Group, Button
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Main, Buy, Sell
from tgbot.misc.switch_inline_query_current_chat import SwitchInlineQueryCurrentChat
from tgbot.models.user import User


async def get_main_text(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.current_context().start_data

    if start_data and (text := start_data.get("start_text")):
        start_data.clear()
        return {"main_text": text}

    return {"main_text": "Что будем делать?"}


async def get_restriction_text(dialog_manager: DialogManager, **_kwargs):
    session = dialog_manager.data.get("session")
    text = "Выберите раздел в который хотите перейти: "
    return {"admin_text": text}


def is_admin(data: Dict, _widget: Whenable, _manager: DialogManager):
    user: User = data.get("middleware_data").get("user")
    return user.role in ('admin', 'owner')


def is_owner(data: Dict, _widget: Whenable, _manager: DialogManager):
    user: User = data.get("middleware_data").get("user")
    return user.role == 'owner'


main_dialog = Dialog(
    Window(
        Format(text="{main_text}", when="main_text"),
        Row(
            Start(
                text=Const("Куплю"),
                id="buy",
                state=Buy.tags
            ),
            Start(
                text=Const("Продам"),
                id="sell",
                state=Sell.tags
            )
        ),
        SwitchTo(
            text=Const("⚜ Панель управления"),
            id="admin_panel",
            state=Main.admin,
            when=is_owner
        ),
        SwitchInlineQueryCurrentChat(
            text=Const("Искать пользователей"),
            id="search_user",
            switch_inline_query_current_chat=Const("пользователи"),
            when=is_admin
        ),
        state=Main.main,
        getter=get_main_text
    ),
    Window(
        Format(text="Выберите раздел в который хотите перейти: "),
        Column(
            Group(
                SwitchTo(
                    text=Const("Ограничения"),
                    id="restrictions",
                    state=Main.restriction
                ),
                SwitchTo(
                    text=Const("Теги"),
                    id="tags",
                    state=Sell.tags,
                ),
                when=is_owner),
            Back(
                text=Const("Назад")
            )),
        state=Main.admin
    ),
    Window(
        Format(text="{restriction_text}", when="restriction_text"),
        Group(
            Row(
                Button(text=Const("<<"), id="subtract", on_click=subtract),
                Button(text=Format("{tag}"), id="subtract"),
                Button(text=Const(">>"), id="add", on_click=add),
            ),
            Row(
                Button(text=Const("<<"), id="subtract", on_click=subtract),
                Button(text=Format("{contact}"), id="subtract"),
                Button(text=Const(">>"), id="add", on_click=add),
            ),
            Row(
                Button(text=Const("<<"), id="subtract", on_click=subtract),
                Button(text=Format("{pic}"), id="subtract"),
                Button(text=Const(">>"), id="add", on_click=add),
            ),
            Row(
                Button(text=Const("<<"), id="subtract", on_click=subtract),
                Button(text=Format("{post}"), id="subtract"),
                Button(text=Const(">>"), id="add", on_click=add),
            ),
        ),
        Back(
            text=Const("Назад")
        ),
        state=Main.restriction,
        getter=get_restriction_text
    )
)
