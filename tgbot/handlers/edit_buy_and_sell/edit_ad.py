from aiogram_dialog import DialogManager

from tgbot.handlers.buy_and_sell.form import get_active_section
from tgbot.misc.ad import Ad

from tgbot.models.post_ad import PostAd


async def get_edit_text(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.current_context().start_data
    widget_data = dialog_manager.current_context().widget_data
    print("super widget_data", widget_data)

    state: list[str] = dialog_manager.current_context().state.state.split(":")

    session = dialog_manager.data.get("session")

    post_id = int(start_data.get("post_id"))
    post_ad: PostAd = await session.get(PostAd, post_id)

    data: dict = {
        "tags": [tag.tag_name for tag in post_ad.tags],
        "description": post_ad.description,
        "contacts": post_ad.contacts.split(","),
        "price": post_ad.price,
        "currency_code": post_ad.currency_code,
        "negotiable": post_ad.negotiable,
        "title": post_ad.title,
        "photos_ids": [m.photo_file_id for m in post_ad.related_messages] if post_ad.related_messages else []
    }

    data.update(widget_data)
    data.pop("post_id", None)

    ad: Ad = Ad(
        state_class=state[0],
        state=state[-1],
        **data
    )

    return {
        "form_text": ad.to_text(where="edit"),
        "page": get_active_section(state[-1]),
        "show_checkbox": state[0] in ("Sell", "EditSell")
    }
