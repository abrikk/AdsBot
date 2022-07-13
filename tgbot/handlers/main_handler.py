from typing import Dict

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, Start
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Main, Buy, Sell, AdminPanel
from tgbot.misc.switch_inline_query_current_chat import SwitchInlineQueryCurrentChat
from tgbot.models.user import User


async def get_main_text(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.current_context().start_data

    if start_data and (text := start_data.get("start_text")):
        user_role = start_data.get("user_role", 'user')
        start_data.clear()
        return {"main_text": text, "user_role": user_role}

    return {"main_text": "Что будем делать?"}


def is_owner(data: Dict, _widget: Whenable, manager: DialogManager):
    if user := manager.data.get("user"):
        return user.role == 'owner'
    else:
        return data.get("user_role") == 'owner'


def is_admin(data: Dict, _widget: Whenable, manager: DialogManager):
    if user := manager.data.get("user"):
        return user.role in ('admin', 'owner')
    else:
        return data.get("user_role") == 'admin'


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
        Start(
            text=Const("⚜ Панель управления"),
            id="admin_panel",
            state=AdminPanel.admin,
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
    )
)
