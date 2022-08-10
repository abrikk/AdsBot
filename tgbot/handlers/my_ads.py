import operator
from datetime import datetime

import pytz
from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Select, ScrollingGroup, Group, Start
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Format, Const

from tgbot.constants import TIME_TO_ASK
from tgbot.misc.states import MyAds, Main, ShowMyAd
from tgbot.models.post_ad import PostAd
from tgbot.services.db_commands import DBCommands


async def get_my_ads_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    my_ads: list = await db.get_my_ads(user_id=dialog_manager.event.from_user.id)
    if not my_ads:
        return {"my_ads_text": "🤷‍♂️ У вас нету опубликованных объявлений."}
    text = f"🔰 Всего объявлений: {len(my_ads)}\n"
    ads_data: list = [(desc, post_id) for desc, post_id in my_ads]

    return {
        "my_ads_text": text,
        "my_ads_data": ads_data,
        "show_scroll": len(my_ads) > 10,
        "show_group": len(my_ads) <= 10
    }


async def show_chosen_ad(_call: types.CallbackQuery, _widget: ManagedWidgetAdapter[Select], manager: DialogManager,
                         post_id: str):
    session = manager.data.get("session")
    post_ad: PostAd = await session.get(PostAd, int(post_id))
    if not (post_ad.created_at + TIME_TO_ASK > datetime.now(pytz.timezone("UTC"))):
        return

    await manager.start(state=ShowMyAd.true, data={"post_id": int(post_id)})


my_ads_dialog = Dialog(
    Window(
        Format(text="{my_ads_text}", when="my_ads_text"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_ads",
                item_id_getter=operator.itemgetter(1),
                items="my_ads_data",
                on_click=show_chosen_ad,
            ),
            id="sg_my_ads",
            width=1,
            height=10,
            when="show_scroll"
        ),
        Group(
            Select(
                Format("{item[0]}"),
                id="s_ads",
                item_id_getter=operator.itemgetter(1),
                items="my_ads_data",
                on_click=show_chosen_ad,
            ),
            id="g_my_ads",
            width=1,
            when="show_group"
        ),
        Start(
            text=Const("🔙 Назад"),
            id="back_to_main",
            state=Main.main,
            mode=StartMode.RESET_STACK
        ),
        state=MyAds.show,
        getter=get_my_ads_text,
        preview_add_transitions=[Start(Const(""), "hint", ShowMyAd.true)]
    )
)
