from aiogram_dialog import DialogManager

from tgbot.handlers.buy_and_sell.form import get_active_section
from tgbot.misc.ad import SalesAd, PurchaseAd

from tgbot.models.post_ad import PostAd
from tgbot.services.db_commands import DBCommands


async def get_edit_text(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.current_context().start_data
    widget_data = dialog_manager.current_context().widget_data

    state = dialog_manager.current_context().state.state.split(":")[-1]

    session = dialog_manager.data.get("session")
    db: DBCommands = dialog_manager.data.get("db_commands")

    post_id = int(start_data.get("post_id"))
    post_ad: PostAd = await session.get(PostAd, post_id)

    tag, contact, pic, post = await db.get_values_of_restrictions()
    limits: dict = {
        "tag_limit": tag,
        "contact_limit": contact,
        "pic_limit": len(post_ad.photos_ids.split(",")) if post_ad.photos_ids else 0,
        "post_limit": post
    }

    data: dict = {
        "tags": [tag.tag_name for tag in post_ad.tags],
        "description": post_ad.description,
        "contacts": post_ad.contacts.split(","),
        "price": post_ad.price,
        "currency_code": post_ad.currency_code,
        "negotiable": post_ad.negotiable,
        "title": post_ad.title,
        "photos_ids": post_ad.photos_ids.split(",") if post_ad.photos_ids else []
    }

    data.update(limits)
    data.update(widget_data)
    data.update({"state": state})
    data.pop("post_id", None)

    if post_ad.post_type == "sell":
        ad = SalesAd(**data)
    else:
        ad = PurchaseAd(**data)

    return {
        "form_text": ad.to_text(where="edit"),
        "page": get_active_section(state),
        "show_checkbox": isinstance(ad, SalesAd)
    }
