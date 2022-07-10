import copy

from aiogram import Bot, types
from aiogram.types import MediaGroup
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from tgbot.config import Config
from tgbot.handlers.buy_and_sell.form import get_active_section, get_current_file_id
from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.misc.states import Main


async def get_form_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    data = copy.deepcopy(widget_data)
    data.pop('currency_code', None)

    state: list[str] = dialog_manager.current_context().state.state.split(":")
    if state[0] == "Sell":
        ad = SalesAd(state=state[-1], **data)
    else:
        ad = PurchaseAd(state=state[-1], **data)

    return {f"{state[0].lower()}_text": ad.to_text(), "page": get_active_section(state[-1])}


async def get_final_text(dialog_manager: DialogManager, **_kwargs):
    state: list[str] = dialog_manager.current_context().state.state.split(":")
    widget_data: dict = dialog_manager.current_context().widget_data
    data: dict = copy.deepcopy(widget_data)

    data.pop('currency_code', None)
    data.pop('current_page', None)
    data.pop('photos_len', None)

    ad = SalesAd(**data) if state[0] == "Sell" else PurchaseAd(**data)

    if ad.photos_ids:
        current_page = widget_data.setdefault('current_page', 1)
    else:
        current_page = None

    if len(ad.photos_ids) > 1:
        widget_data['photos_len'] = len(ad.photos_ids)

    return {
        "final_text": ad.preview() if state[1] == "preview" else ad.confirm(),
        "file_id": get_current_file_id(ad.photos_ids, current_page),
        "show_scroll": len(ad.photos_ids) > 1,
        "photo_text": len(ad.photos_ids) > 1 and current_page and f"{current_page}/{len(ad.photos_ids)}"
    }


async def on_confirm(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    obj = manager.event
    bot: Bot = obj.bot
    state: str = manager.current_context().state.state.split(":")[0]
    widget_data = manager.current_context().widget_data
    config: Config = manager.data.get("config")

    data = copy.deepcopy(widget_data)
    data.pop('currency_code', None)
    data.pop('current_page', None)
    data.pop('photos_len', None)
    data.update({"mention": obj.from_user.get_mention()})

    ad = SalesAd(**data) if state == "Sell" else PurchaseAd(**data)

    album = MediaGroup()

    if ad.photos_ids:
        for file_id in ad.photos_ids[:-1]:
            album.attach_photo(photo=file_id)

        album.attach_photo(photo=ad.photos_ids[-1], caption=ad.post())

        await bot.send_media_group(chat_id=config.tg_bot.channel_id,
                                   media=album)
    else:
        await bot.send_message(chat_id=config.tg_bot.channel_id,
                               text=ad.post())

    await call.answer("Объявление было успешно опубликовано в канале!")
    await manager.start(Main.main, mode=StartMode.RESET_STACK)
