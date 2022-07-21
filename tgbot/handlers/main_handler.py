from typing import Dict

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, SwitchTo, Group, Back
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Main, AdminPanel, MyAds, Form
from tgbot.misc.switch_inline_query_current_chat import SwitchInlineQueryCurrentChat


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
        return data.get("user_role") in ('admin', 'owner')


main_dialog = Dialog(
    Window(
        Format(text="{main_text}", when="main_text"),
        SwitchTo(
          text=Const("🪄 Создать объявление"),
          id="make_ad",
          state=Main.make_ad
        ),
        # Row(
        #     Start(
        #         text=Const("🟠 Куплю"),
        #         id="buy",
        #         state=Buy.tags
        #     ),
        #     Start(
        #         text=Const("🔴 Продам"),
        #         id="sell",
        #         state=Sell.tags
        #     )
        # ),
        Start(
            text=Const("🌀 Мои объявления"),
            id="my_ads",
            state=MyAds.show
        ),
        Start(
            text=Const("⚜ Панель управления"),
            id="admin_panel",
            state=AdminPanel.admin,
            when=is_owner
        ),
        SwitchInlineQueryCurrentChat(
            text=Const("👥 Искать пользователей"),
            id="search_user",
            switch_inline_query_current_chat=Const("пользователи"),
            when=is_admin
        ),
        state=Main.main,
        getter=get_main_text
    ),
    Window(
        Const("Выберите рубрику вашего объявления:"),
        Group(
            Start(
                text=Const("🟠 Куплю"),
                id="buy",
                state=Form.category,
                data={"heading": "buy"}
            ),
            Start(
                text=Const("🔴 Продам"),
                id="sell",
                state=Form.category,
                data={"heading": "sell"}
            ),
            Start(
                text=Const("🟡 Сниму"),
                id="occupy",
                state=Form.category,
                data={"heading": "occupy"}
            ),
            Start(
                text=Const("🟢 Сдам"),
                id="rent",
                state=Form.category,
                data={"heading": "rent"}
            ),
            Start(
                text=Const("🔃 Обменяю"),
                id="exchange",
                state=Form.category,
                data={"heading": "exchange"}
            ),
            width=2
        ),
        Back(
          text=Const("🔚 В главное меню")
        ),
        state=Main.make_ad
    )
)
