import operator
from datetime import timedelta, datetime
from typing import Any, Dict

from aiogram import Dispatcher, types
from aiogram.utils.markdown import hcode
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Start, Radio, Checkbox, Button, Group, Counter, ManagedCounterAdapter, \
    ManagedCheckboxAdapter
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.when import Whenable

from tgbot.constants import OWNER, ADMIN, USER, BANNED
from tgbot.filters.inline_filter import InlineFilter
from tgbot.misc.states import Main, ShowUser
from tgbot.models.user import User
from tgbot.services.db_commands import DBCommands


async def start_show_user_dialog(message: types.Message, dialog_manager: DialogManager):
    user_id = message.text.split(":")[-1].strip()
    await dialog_manager.start(
        state=ShowUser.true,
        data={"user_id": user_id},
        mode=StartMode.RESET_STACK
    )


async def set_default_data(_, dialog_manager: DialogManager):
    user_id: int = int(dialog_manager.current_context().start_data.get("user_id"))
    db: DBCommands = dialog_manager.data.get("db_commands")
    post_limit: int = await db.get_value_of_restriction("post")
    user_role: str = await db.get_user_role(user_id)
    user_post_limit: int = await db.get_user_post_limit(user_id)
    checked = True if (not user_post_limit) or user_post_limit == post_limit else False

    value = user_post_limit if user_post_limit else post_limit

    await dialog_manager.dialog().find('user_role').set_checked(event="", item_id=user_role)
    await dialog_manager.dialog().find('default_post_limit').set_checked(event="", checked=checked)
    await dialog_manager.dialog().find('post_limit_counter').set_value(value=value)


async def get_show_user_text(dialog_manager: DialogManager, **_kwargs) -> dict:
    user_id: int = int(dialog_manager.current_context().start_data.get("user_id"))
    session = dialog_manager.data.get("session")
    user: User = await session.get(User, user_id)
    if user.restricted_till:
        restricted_till = f"{user.restricted_till.strftime('%d.%m.%Y %H:%M:%S')}\n"
    else:
        restricted_till = "нет ограничений\n"

    user_text = ("🆔 ID пользователя: {id}\n"
                 "👤 Пользователь: <code>{name}</code>\n"
                 "📯 Роль: {role}\n"
                 "⚠️ Ограничен до: {restricted_till}"
                 "🗓 Дата регистрации: {created_at}").format(
        id=hcode(user.user_id),
        name=user.first_name + (user.last_name and " " + user.last_name or ""),
        role=hcode(user.role),
        restricted_till=hcode(restricted_till),
        created_at=hcode(user.created_at.strftime('%d.%m.%Y %H:%M:%S'))
    )
    available_roles = (
        ("Владелец", OWNER),
        ("Администратор", ADMIN),
        ("Пользователь", USER),
        ("Забанен", BANNED)
    )

    restrict_options: list = [(i + 'д', i) for i in ('1', '3', '7', '14', '30')]

    return {"user_text": user_text, "user_roles": available_roles,
            "restrict_options": restrict_options}


async def change_user_role(call: types.CallbackQuery, _widget: Any, manager: DialogManager, role: str):
    user_id: int = int(manager.current_context().start_data.get("user_id"))
    db: DBCommands = manager.data.get("db_commands")
    await db.update_user_role(user_id, role)
    await call.answer("Роль пользователя изменена на: " + role)


async def remove_restrictions(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    user_id: int = int(manager.current_context().start_data.get("user_id"))
    session = manager.data.get("session")
    user: User = await session.get(User, user_id)
    if user.restricted_till:
        user.restricted_till = None
        await session.commit()
        await call.answer("Ограничения удалены")
    else:
        await call.answer("У этого пользователя нет ограничений")


def show_restrict(_data: Dict, _widget: Whenable, manager: DialogManager) -> bool:
    return manager.current_context().widget_data.get("restrict") is True


def show_post_limit(_data: Dict, _widget: Whenable, manager: DialogManager) -> bool:
    return manager.current_context().widget_data.get("post_limit") is True


async def restrict_user(call: types.CallbackQuery, _widget: Any, manager: DialogManager, days: str):
    user_id: int = int(manager.current_context().start_data.get("user_id"))
    session = manager.data.get("session")
    user: User = await session.get(User, user_id)

    user.restricted_till = datetime.today() + timedelta(days=int(days))
    await session.commit()
    await call.answer("Пользователь ограничен на: " + days + " дней")
    manager.current_context().widget_data["restrict"] = False


async def change_post_limit_value(_call: types.CallbackQuery, widget: ManagedCounterAdapter, manager: DialogManager):
    user_id: int = int(manager.current_context().start_data.get("user_id"))
    session = manager.data.get("session")
    db: DBCommands = manager.data.get("db_commands")
    user: User = await session.get(User, user_id)
    user.post_limit = int(widget.get_value())
    post_limit: int = await db.get_value_of_restriction("post")

    if user.post_limit == post_limit:
        user.post_limit = None
    checked: bool = True if (not user.post_limit) or user.post_limit == post_limit else False
    await manager.dialog().find('default_post_limit').set_checked(event="", checked=checked)
    await session.commit()


async def set_default_post_limit(call: types.CallbackQuery, widget: ManagedCheckboxAdapter, manager: DialogManager):
    is_checked: bool = not widget.is_checked()
    await widget.set_checked(event=call, checked=is_checked)
    user_id: int = int(manager.current_context().start_data.get("user_id"))
    session = manager.data.get("session")
    db: DBCommands = manager.data.get("db_commands")
    user: User = await session.get(User, user_id)
    post_limit: int = await db.get_value_of_restriction("post")
    user.post_limit = None
    await manager.dialog().find('post_limit_counter').set_value(value=post_limit)
    await session.commit()
    manager.current_context().widget_data["post_limit"] = False


show_user_dialog = Dialog(
    Window(
        Format(text="{user_text}", when="user_text"),
        Button(
            text=Const("🗑 Убрать ограничения"),
            id="remove_restrictions",
            on_click=remove_restrictions
        ),
        Checkbox(
            checked_text=Const("🔘 Ограничить"),
            unchecked_text=Const("⚪️ Ограничить"),
            id="restrict"
        ),
        Radio(
            Format("☑️ {item[0]}"),
            Format("{item[0]}"),
            id="user_restrict_options",
            item_id_getter=operator.itemgetter(1),
            items="restrict_options",
            when=show_restrict,
            on_click=restrict_user
        ),
        Checkbox(
            checked_text=Const("🔘 Изменить лимит постов в день"),
            unchecked_text=Const("⚪️ Изменить лимит постов в день"),
            id="post_limit"
        ),
        Group(
            Counter(
                id="post_limit_counter",
                text=Format("{value}"),
                min_value=1,
                on_value_changed=change_post_limit_value
            ),
            Checkbox(
                checked_text=Const("✔️ По умолчанию"),
                unchecked_text=Const("️ По умолчанию"),
                id="default_post_limit",
                on_state_changed=set_default_post_limit
            ),
            when=show_post_limit
        ),
        Group(
            Radio(
                checked_text=Format("✔️ {item[0]}"),
                unchecked_text=Format("{item[0]}"),
                id="user_role",
                item_id_getter=operator.itemgetter(1),
                items="user_roles",
                on_click=change_user_role
            ),
            width=2
        ),
        Start(
            text=Const("🔚 В главное меню"),
            id="to_main",
            state=Main.main,
            mode=StartMode.RESET_STACK
        ),
        state=ShowUser.true,
        getter=get_show_user_text
    ),
    on_start=set_default_data
)


def register_show_product(dp: Dispatcher):
    dp.register_message_handler(start_show_user_dialog, InlineFilter())
