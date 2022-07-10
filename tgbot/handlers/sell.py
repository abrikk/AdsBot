import copy

from aiogram import types, Bot
from aiogram.types import MediaGroup
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from tgbot.config import Config
from tgbot.handlers.form import get_current_file_id, get_active_section
from tgbot.misc.ad import SalesAd
from tgbot.misc.states import Main


async def get_sell_text(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.current_context().widget_data
    sell_data = copy.deepcopy(data)
    sell_data.pop('currency_code', None)

    state = dialog_manager.current_context().state.state.split(":")[-1]

    sell_ad = SalesAd(state=state, **sell_data)

    return {"sell_text": sell_ad.to_text(), "page": get_active_section(state)}


async def get_sell_final_text(dialog_manager: DialogManager, **_kwargs):
    state: str = dialog_manager.current_context().state.state.split(":")[-1]
    widget_data: dict = dialog_manager.current_context().widget_data
    sell_data: dict = copy.deepcopy(widget_data)

    sell_data.pop('currency_code', None)
    sell_data.pop('current_page', None)
    sell_data.pop('photos_len', None)

    sell_ad = SalesAd(**sell_data)

    if sell_ad.photos_ids:
        current_page = widget_data.setdefault('current_page', 1)
    else:
        current_page = None

    if len(sell_ad.photos_ids) > 1:
        widget_data['photos_len'] = len(sell_ad.photos_ids)

    return {
        "final_text": sell_ad.preview() if state == "preview" else sell_ad.confirm(),
        "file_id": get_current_file_id(sell_ad.photos_ids, current_page),
        "show_scroll": len(sell_ad.photos_ids) > 1,
        "photo_text": len(sell_ad.photos_ids) > 1 and current_page and f"{current_page}/{len(sell_ad.photos_ids)}"
    }


async def on_confirm(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    obj = manager.event
    bot: Bot = obj.bot
    widget_data = manager.current_context().widget_data
    config: Config = manager.data.get("config")

    sell_data = copy.deepcopy(widget_data)
    sell_data.pop('currency_code', None)
    sell_data.pop('current_page', None)
    sell_data.pop('photos_len', None)
    sell_data.update({"mention": obj.from_user.get_mention()})

    sell_ad = SalesAd(**sell_data)

    album = MediaGroup()

    if sell_ad.photos_ids:
        for file_id in sell_ad.photos_ids[:-1]:
            album.attach_photo(photo=file_id)

        album.attach_photo(photo=sell_ad.photos_ids[-1], caption=sell_ad.post())

        await bot.send_media_group(chat_id=config.tg_bot.channel_id,
                                   media=album)
    else:
        await bot.send_message(chat_id=config.tg_bot.channel_id,
                               text=sell_ad.post())

    await call.answer("Объявление было успешно опубликовано в канале!")
    await manager.start(Main.main, mode=StartMode.RESET_STACK)

#

