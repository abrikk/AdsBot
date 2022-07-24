import logging
import operator
from datetime import timedelta, datetime
from typing import Any, Dict

from aiogram import Dispatcher, types
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.markdown import hcode
from aiogram_dialog import DialogManager, Dialog, Window, StartMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Start, Radio, Checkbox, Button, Group, Counter, ManagedCounterAdapter, \
    ManagedCheckboxAdapter, Row, Next
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.when import Whenable
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.constants import OWNER, ADMIN, USER, BANNED
from tgbot.filters.inline_filter import InlineFilter
from tgbot.filters.is_user import IsUser
from tgbot.handlers.create_ad.form import when_not, get_user_mention
from tgbot.misc.states import Main, ShowUser
from tgbot.models.post_ad import PostAd
from tgbot.models.user import User
from tgbot.services.db_commands import DBCommands


async def start_show_user_dialog(message: types.Message, dialog_manager: DialogManager):
    user_id = message.text.split(":")[-1].strip()
    await dialog_manager.start(
        state=ShowUser.true,
        data={"user_id": int(user_id)},
        mode=StartMode.RESET_STACK
    )


async def set_default_data(_, dialog_manager: DialogManager):
    user_id: int = dialog_manager.current_context().start_data.get("user_id")
    db: DBCommands = dialog_manager.data.get("db_commands")
    post_limit: int = await db.get_value_of_restriction("post")
    user_role: str = await db.get_user_role(user_id)
    user_post_limit: int = await db.get_user_post_limit(user_id)
    checked: bool = True if (not user_post_limit) or user_post_limit == post_limit else False

    value = user_post_limit if user_post_limit else post_limit

    dialog_manager.current_context().widget_data["default_role"] = user_role
    await dialog_manager.dialog().find('user_role').set_checked(event="", item_id=user_role)
    await dialog_manager.dialog().find('default_post_limit').set_checked(event="", checked=checked)
    await dialog_manager.dialog().find('post_limit_counter').set_value(value=value)


async def get_show_user_text(dialog_manager: DialogManager, **_kwargs) -> dict:
    searched_user_id: int = dialog_manager.current_context().start_data.get("user_id")
    session = dialog_manager.data.get("session")
    user: User = dialog_manager.data.get("user")
    searched_user: User = await session.get(User, searched_user_id)
    if searched_user.restricted_till:
        restricted_till = f"{searched_user.restricted_till.strftime('%d.%m.%Y %H:%M:%S')}\n"
    else:
        restricted_till = "нет ограничений\n"

    user_text = ("🆔 ID пользователя: {id}\n"
                 "👤 Пользователь: <code>{name}</code>\n"
                 "📯 Роль: {role}\n"
                 "⚠️ Ограничен до: {restricted_till}"
                 "🗓 Дата регистрации: {created_at}").format(
        id=hcode(searched_user.user_id),
        name=searched_user.first_name + (searched_user.last_name and " " + searched_user.last_name or ""),
        role=hcode(searched_user.role),
        restricted_till=hcode(restricted_till),
        created_at=hcode(searched_user.created_at.strftime('%d.%m.%Y %H:%M:%S'))
    )
    available_roles = [
        ("Пользователь", USER),
        ("Забанен", BANNED)
    ]
    if user.role == OWNER:
        available_roles.append(("Администратор", ADMIN))

    if role := dialog_manager.current_context().widget_data.get("user_role"):
        user_text = f"Вы уверены что хотите изменить роль пользователя на {role}?\n\n" + user_text

    restrict_options: list = [(i + 'д', i) for i in ('1', '3', '7', '14', '30')]

    return {"user_text": user_text, "user_roles": available_roles,
            "restrict_options": restrict_options}


async def get_input_reason(dialog_manager: DialogManager, **_kwargs) -> dict:
    widget_data = dialog_manager.current_context().widget_data
    ban_reason: str = widget_data.get("ban_reason")
    if not ban_reason:
        input_reason = "Введите причину блокировки пользователя или пропустите этот этап:"

    else:
        input_reason = "Вы уверены что хотите заблокировать этого пользователя?" \
                       "(пользователь будет заблокирован в канале и бот" \
                       " не будет доступен)\n\n" \
                       "Причина блокировки: {ban_reason}".format(ban_reason=ban_reason)

    return {"input_reason": input_reason}


async def get_conditions(dialog_manager: DialogManager, **_kwargs) -> dict:
    context = dialog_manager.current_context()
    is_banned: bool = context.widget_data.get("user_role") == BANNED
    ban_reason: str = context.widget_data.get("ban_reason")
    return {"is_banned": is_banned, "ban_reason": ban_reason}


async def change_user_role(call: types.CallbackQuery, _widget: Any, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    user_id: int = manager.current_context().start_data.get("user_id")
    db: DBCommands = manager.data.get("db_commands")
    role = widget_data.get("user_role")

    await db.update_user_role(user_id, role)
    await call.answer("Роль пользователя изменена на: " + role)
    print(widget_data.get("default_role"))
    if role == BANNED:
        support_ids: list[int, str, str | None, str | None] = await db.get_support_team()
        support_mentions: str = ", ".join([
            get_user_mention(id, first_name, last_name, username)
            for id, first_name, last_name, username in support_ids
        ])

        ban_reason: str = widget_data.get("ban_reason")
        session = manager.data.get("session")
        scheduler: AsyncIOScheduler = call.bot.get("scheduler")
        config: Config = manager.data.get("config")
        post_ids: list[int] = await db.get_user_posts_ids(user_id)

        for id in post_ids:
            post_ad: PostAd = await session.get(PostAd, id)

            try:
                if post_ad.related_messages:
                    for message in post_ad.related_messages:
                        await call.bot.delete_message(
                            chat_id=config.tg_bot.channel_id,
                            message_id=message.message_id
                        )
                else:
                    await call.bot.delete_message(
                        chat_id=config.tg_bot.channel_id,
                        message_id=post_ad.post_id
                    )
            except MessageToDeleteNotFound:
                logging.warning("Message to delete not found")

            try:
                scheduler.remove_job("ask_" + str(post_ad.post_id))
                scheduler.remove_job("check_" + str(post_ad.post_id))
            except JobLookupError:
                logging.warning("Job not found")

            await session.delete(post_ad)

        else:
            await session.commit()
            is_admin: bool = (await call.bot.get_chat_member(config.tg_bot.channel_id,
                                                             call.from_user.id)).is_chat_admin()
            if not is_admin:
                await call.bot.ban_chat_member(
                    chat_id=config.tg_bot.channel_id,
                    user_id=user_id
                )

            ban_text = f"Вы были заблокированы{ban_reason and ' по причине: ' + ban_reason or '.'}\n" \
                       f"Если вы считаете это ошибка, пожалуйста, " \
                       f"обратитесь в поддержку: {support_mentions}"

            await call.bot.send_message(
                chat_id=user_id,
                text=ban_text,
                disable_web_page_preview=True
            )

            await call.answer("Пользователь был успешно заблокирован!")

    widget_data["default_role"] = role
    await manager.dialog().find('user_role').set_checked(event="", item_id=role)
    await manager.switch_to(ShowUser.true)


async def save_user_role(_call: types.CallbackQuery, _widget: Any, manager: DialogManager, role: str):
    widget_data = manager.current_context().widget_data
    if role != widget_data.get("default_role"):
        widget_data["user_role"] = role
        await manager.dialog().next()


async def clear_user_role(_call: types.CallbackQuery, _widget: Any, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    widget_data.pop("user_role")
    user_role = widget_data.get("default_role")
    await manager.dialog().find('user_role').set_checked(event="", item_id=user_role)
    await manager.switch_to(ShowUser.true)


async def clear_input(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    manager.current_context().widget_data.pop("ban_reason")


async def remove_restrictions(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    user_id: int = manager.current_context().start_data.get("user_id")
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
    user_id: int = manager.current_context().start_data.get("user_id")
    session = manager.data.get("session")
    user: User = await session.get(User, user_id)

    user.restricted_till = datetime.today() + timedelta(days=int(days))
    await session.commit()
    await call.answer("Пользователь ограничен на: " + days + " дней")
    manager.current_context().widget_data["restrict"] = False


async def change_post_limit_value(_call: types.CallbackQuery, widget: ManagedCounterAdapter, manager: DialogManager):
    user_id: int = manager.current_context().start_data.get("user_id")
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


async def set_default_post_limit(_call: types.CallbackQuery, _widget: ManagedCheckboxAdapter, manager: DialogManager):
    user_id: int = manager.current_context().start_data.get("user_id")
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
                checked_text=Format("✅️ {item[0]}"),
                unchecked_text=Format("⬜️ {item[0]}"),
                id="user_role",
                item_id_getter=operator.itemgetter(1),
                items="user_roles",
                on_click=save_user_role
            ),
            width=2
        ),
        Start(
            text=Const("🔚 В главное меню"),
            id="to_main",
            state=Main.main,
            mode=StartMode.RESET_STACK
        ),
        state=ShowUser.true
    ),

    Window(
        Format(text="{user_text}", when="user_text"),
        Row(
            Button(
                text=Const("Отмена"),
                id="cancel_role",
                on_click=clear_user_role
            ),
            Button(
                text=Const("Да ✅"),
                id="save_role",
                on_click=change_user_role,
                when=when_not("is_banned")
            ),
            Next(
                text=Const("Да ✅"),
                when="is_banned"
            )
        ),
        state=ShowUser.confirm,
        getter=get_conditions
    ),
    Window(
        Format("{input_reason}", when="input_reason"),
        Row(
            Button(
                text=Const("Отмена"),
                id="cancel_ban",
                on_click=clear_user_role
            ),
            Button(
                text=Const("Пропустить"),
                id="skip_reason",
                on_click=change_user_role,
                when=when_not("ban_reason")
            ),
            Button(
                text=Const("Очистить"),
                id="clear_input",
                on_click=clear_input,
                when="ban_reason"
            ),
        ),
        Button(
            text=Const("Подтвердить"),
            id="confirm_ban",
            on_click=change_user_role,
            when="ban_reason"
        ),
        TextInput(
            id="ban_reason"
        ),
        state=ShowUser.reason,
        getter=[get_conditions, get_input_reason]
    ),
    on_start=set_default_data,
    getter=get_show_user_text
)


def register_show_product(dp: Dispatcher):
    dp.register_message_handler(start_show_user_dialog, InlineFilter(), IsUser())
