from typing import Dict

from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Group, Back, Button, Next
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Main, AdminPanel, MyAds, Form
from tgbot.misc.switch_inline_query_current_chat import SwitchInlineQueryCurrentChat
from tgbot.models.user import User
from tgbot.services.db_commands import DBCommands


async def get_main_text(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.current_context().start_data

    if start_data and (text := start_data.get("start_text")):
        user_role = start_data.get("user_role", 'user')
        start_data.clear()
        return {"main_text": text, "user_role": user_role}

    return {"main_text": "Что будем делать?"}


async def switch_to_make_ad(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    session = manager.data.get("session")
    user: User = await session.get(User, manager.event.from_user.id)

    if restricted_date := user.restricted_till:
        date_text = "Администраторы бота запретили Вам создавать объявления до {date}, " \
                    "{time}".format(date=restricted_date.strftime("%d.%m.%Y"),
                                    time=restricted_date.strftime("%H:%M"))
        await call.answer(text=date_text, show_alert=True)
        return

    db: DBCommands = manager.data.get("db_commands")
    global_max_active: int = await db.get_value_of_restriction(uid="max_active")
    user_current_active: int = await db.count_user_active_ads(user_id=user.user_id)

    if user.max_active and user_current_active >= user.max_active or not user.max_active and user_current_active >= global_max_active:
        await call.answer(text="Вы достигли максимальный лимит активных объявлений.", show_alert=True)
        return

    common_post_limit: int = await db.get_post_limit()

    if user.post_limit and user.posted_today >= user.post_limit or not user.post_limit and user.posted_today >= common_post_limit:
        await call.answer(text="Вы исчерпали лимит публикаций объявлений в день. Попробуйте завтра.", show_alert=True)
        return

    await manager.dialog().next()


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
        Button(
            text=Const("🪄 Создать объявление"),
            id="make_ad",
            on_click=switch_to_make_ad
        ),
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
        getter=get_main_text,
        preview_add_transitions=[Next()]
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
