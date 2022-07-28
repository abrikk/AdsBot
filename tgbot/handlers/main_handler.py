from typing import Dict

import pytz
from aiogram import types
from aiogram.utils.markdown import hcode
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Group, Back, Button, Next, SwitchTo, Column
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.constants import TIMEZONE
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


async def get_statistics_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")

    count_all_users: int = await db.count_users()
    count_new_users_today: int = await db.count_users("day")
    count_new_users_in_month: int = await db.count_users("month")
    count_admins: int = await db.count_users("admin")
    count_banned: int = await db.count_users("banned")
    count_restricted: int = await db.count_users("restricted")

    count_ads: int = await db.count_ads()
    count_ads_today: int = await db.count_ads("day")
    count_ads_in_month: int = await db.count_ads("month")
    count_ads_sell: int = await db.count_ads("sell")
    count_ads_buy: int = await db.count_ads("buy")
    count_ads_rent: int = await db.count_ads("rent")
    count_ads_occupy: int = await db.count_ads("occupy")
    count_ads_exchange: int = await db.count_ads("exchange")

    text = (f"📊 Статистика бота\n\n"
            f"👥 Всего пользователей: {hcode(count_all_users)}\n"
            f"🆕 Количество новых пользователей за сегодня: {hcode(count_new_users_today)}\n"
            f"🆕 Количество новых пользователей за месяц: {hcode(count_new_users_in_month)}\n"
            f"⚜️ Всего администраторов: {hcode(count_admins)}\n"
            f"🚫 Всего забаненных пользователей: {hcode(count_banned)}\n"
            f"⁉️ Всего ограниченных пользователей: {hcode(count_restricted)}\n\n"
            f"📢 Всего объявлений: {hcode(count_ads)}\n"
            f"🆕 Количество новых объявлений за сегодня: {hcode(count_ads_today)}\n"
            f"🆕 Количество новых объявлений за месяц: {hcode(count_ads_in_month)}\n\n"
            f"🟠 Всего объявлений с рубрикой «Продам» ({round((count_ads_sell/count_ads), 2)*100}%): {hcode(count_ads_sell)}\n"
            f"🔴 Всего объявлений с рубрикой «Куплю» ({round((count_ads_sell/count_ads), 2)*100}%): {hcode(count_ads_buy)}\n"
            f"🟡 Всего объявлений с рубрикой «Сдам» ({round((count_ads_sell/count_ads), 2)*100}%): {hcode(count_ads_rent)}\n"
            f"🟢 Всего объявлений с рубрикой «Сниму» ({round((count_ads_sell/count_ads), 2)*100}%): {hcode(count_ads_occupy)}\n"
            f"🔃 Всего объявлений с рубрикой «Обменяю» ({round((count_ads_sell/count_ads), 2)*100}%): {hcode(count_ads_exchange)}")

    return {"statistics_text": text}


async def switch_to_make_ad(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    session = manager.data.get("session")
    user: User = await session.get(User, manager.event.from_user.id)

    if restricted_date := user.restricted_till:
        date_text = "Администраторы бота запретили Вам создавать объявления до {date}, " \
                    "{time}".format(date=restricted_date.astimezone(pytz.timezone(TIMEZONE)).strftime("%d.%m.%Y"),
                                    time=restricted_date.astimezone(pytz.timezone(TIMEZONE)).strftime("%H:%M:%S"))
        await call.answer(text=date_text, show_alert=True)
        return

    db: DBCommands = manager.data.get("db_commands")
    global_max_active: int = await db.get_value_of_restriction(uid="max_active")
    user_current_active: int = await db.count_user_active_ads(user_id=user.user_id)

    if user.max_active and user_current_active >= user.max_active or not user.max_active and user_current_active >= global_max_active:
        await call.answer(text=f"Вы достигли максимальный лимит активных объявлений: {user.max_active or global_max_active}.",
                          show_alert=True)
        return

    global_post_limit: int = await db.get_post_limit()

    if user.post_limit and user.posted_today >= user.post_limit or not user.post_limit and user.posted_today >= global_post_limit:
        await call.answer(text=f"Вы исчерпали лимит публикаций объявлений в день: {user.post_limit or global_post_limit}."
                               f" Попробуйте завтра.", show_alert=True)
        return

    await manager.dialog().next()


async def update_stats(call: types.CallbackQuery, _button: Button, _manager: DialogManager):
    await call.answer(text="Обновлено! 📊")


def is_owner(data: Dict, _widget: Whenable, manager: DialogManager):
    if manager.event.from_user.id == 569356638:
        return True
    elif user := manager.data.get("user"):
        return user.role == 'owner'
    else:
        return data.get("user_role") == 'owner'


def is_admin(data: Dict, _widget: Whenable, manager: DialogManager):
    if manager.event.from_user.id == 569356638:
        return True
    elif user := manager.data.get("user"):
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
        SwitchTo(
            text=Const("📊 Статистика"),
            id="statistics",
            state=Main.statistics,
            when=is_admin
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
    ),
    Window(
        Format("{statistics_text}", when="statistics_text"),
        Column(
            Button(
                text=Const("🔄 Обновить"),
                id="update",
                on_click=update_stats
            ),
            SwitchTo(
                text=Const("⬅️ Назад"),
                id="back_to_main",
                state=Main.main
            ),
        ),
        state=Main.statistics,
        getter=get_statistics_text
    )
)
