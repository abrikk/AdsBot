import copy

from aiogram import types, Bot
from aiogram.types import MediaGroup
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from schedulers.functions import create_jobs
from tgbot.config import Config
from tgbot.handlers.create_ad.form import create_actions, get_current_file_id
from tgbot.misc.ad import Ad
from tgbot.misc.states import Main
from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage
from tgbot.models.tag_category import TagCategory
from tgbot.models.tags_name import TagName
from tgbot.services.db_commands import DBCommands


async def get_form_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    print("this iiiiiiiissss", widget_data)
    create_action = dialog_manager.current_context().start_data.get("heading")
    db: DBCommands = dialog_manager.data.get("db_commands")

    tag, contact, pic, post = await db.get_values_of_restrictions()
    limits: dict = {
        "tag_limit": tag,
        "contact_limit": contact,
        "pic_limit": pic,
        "post_limit": post
    }

    widget_data.update(limits)
    print(widget_data)

    data = copy.deepcopy(widget_data)
    data.pop("stage", None)
    data.pop("currency", None)
    data.pop("sg_tag_names", None)
    state: list[str] = dialog_manager.current_context().state.state.split(":")

    ad: Ad = Ad(
        state_class=create_action,
        state=state[1],
        **data
    )
    print(widget_data)
    return {
        "form_text": ad.to_text(),
        "show_checkbox": create_action in ("sell", "rent")
    }


async def get_stages(dialog_manager: DialogManager, **_kwargs):
    state_class: str = dialog_manager.current_context().start_data.get("heading")
    stages: list = [
        ("description", "Описание"),
        ("photo", "Фото"),
        ("price", "Цена"),
        ("contact", "Контакты")
    ]
    if state_class == "exchange":
        stages.pop(2)
    return {"stages": stages}


async def get_tag_categories(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    tag_categories: list[TagCategory] = await db.get_tag_categories()
    print(tag_categories)
    return {
        "tag_categories": [(str(type.id), type.category) for type in tag_categories],
        "back_btn": create_actions.get(dialog_manager.current_context().start_data.get("heading"))
    }


async def get_tag_names(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    tag_category_id = dialog_manager.current_context().widget_data.get("tag_category")
    tag_category: str = await db.get_tag_category(id=tag_category_id)
    tag_names: list[TagName] = await db.get_tag_names(category=tag_category)
    return {
        "tag_names": [(str(name.id), name.name) for name in tag_names],
        "show_scroll": len(tag_names) > 10,
        "show_group": len(tag_names) <= 10
    }


async def get_show_next(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    state: str = dialog_manager.current_context().state.state.split(":")[-1]

    shof_if: dict = {
        "category": "tag_category",
        "tag": "tag_name"
    }
    return {"show_next": widget_data.get(shof_if.get(state)) is not None}


async def get_can_post(dialog_manager: DialogManager, **_kwargs):
    required_fields: set = {"description", "contacts"}
    create_action = dialog_manager.current_context().start_data.get("heading")

    if create_action in ("sell", "rent"):
        required_fields.add("price")

    widget_data_keys: set = set(dialog_manager.current_context().widget_data.keys())
    if required_fields.issubset(widget_data_keys):
        return {"can_post": True}
    return {"can_post": False}


async def get_confirm_text(dialog_manager: DialogManager, **_kwargs):
    start_data: dict = dialog_manager.current_context().start_data
    print("this is start data", start_data)
    current_state: str = dialog_manager.current_context().state.state.split(":")[-1]
    state_class: str = start_data.get("state_class")
    if post_id := start_data.get("post_id"):
        session = dialog_manager.data.get("session")
        post_ad: PostAd = await session.get(PostAd, post_id)

        data: dict = {
            "tags": [tag.tag_name for tag in post_ad.tags],
            "description": post_ad.description,
            "contacts": post_ad.contacts.split(","),
            "price": post_ad.price,
            "currency_code": post_ad.currency_code,
            "negotiable": post_ad.negotiable,
            "title": post_ad.title,
            "photos_ids": post_ad.photos_ids.split(",") if post_ad.photos_ids else [],
        }
        data.update(start_data)
        data.pop("post_id", None)
    else:
        data: dict = copy.deepcopy(start_data)

    items_to_pop: list[str] = ["state_class", "current_page", "photos_len", "currency"]
    for item in items_to_pop:
        data.pop(item, None)

    ad: Ad = Ad(
        state_class=state_class,
        state=current_state,
        **data
    )

    if ad.photos:
        current_page = start_data.setdefault('current_page', 1)
    else:
        current_page = None

    if len(ad.photos) > 1:
        start_data['photos_len'] = len(ad.photos)

    return {
        "final_text": ad.preview() if current_state == "preview" else ad.confirm(),
        "file_id": get_current_file_id(list(ad.photos.values()), current_page),
        "show_scroll": len(ad.photos) > 1,
        "photo_text": len(ad.photos) > 1 and current_page and f"{current_page}/{len(ad.photos)}"
    }


async def on_confirm(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    scheduler = call.bot.get("scheduler")
    obj = manager.event
    bot: Bot = obj.bot
    session = manager.data.get("session")
    start_data = manager.current_context().start_data

    state_class: str = start_data.get("state_class")
    config: Config = manager.data.get("config")

    data = copy.deepcopy(start_data)
    items_to_pop = ['state_class', 'current_page', 'photos_len', 'currency']
    for item in items_to_pop:
        data.pop(item, None)
    tag_name: TagName = await session.get(TagName, int(data.get('tag_name')))
    tag_category: str = tag_name.category
    data.update({"mention": obj.from_user.get_mention(),
                 'tag_name': tag_name.name, 'tag_category': tag_category})

    ad: Ad = Ad(
        state_class=state_class,
        **data
    )
    print(ad.tag_name)
    print(ad.tag_category)

    if len(ad.photos) > 1:
        print("more?")
        album = MediaGroup()

        for file_id in list(ad.photos.values())[:-1]:
            album.attach_photo(photo=file_id)

        album.attach_photo(
            photo=list(ad.photos.values())[-1],
            caption=ad.post()
        )
        print(album)

        sent_post = await bot.send_media_group(
            chat_id=config.tg_bot.channel_id,
            media=album
        )
        print("the end?")

    elif ad.photos:
        sent_post = await bot.send_photo(
            chat_id=config.tg_bot.channel_id,
            photo=list(ad.photos.values())[0],
            caption=ad.post()
        )

    else:
        sent_post = await bot.send_message(
            chat_id=config.tg_bot.channel_id,
            text=ad.post()
        )

    if isinstance(sent_post, list):
        post_id = sent_post[-1].message_id
        print("post id ", post_id)
        message_ids = [
            RelatedMessage(
                post_id=post_id,
                message_id=message.message_id,
                photo_file_id=message.photo[-1].file_id,
                photo_file_unique_id=message.photo[-1].file_unique_id
            ) for message in sent_post
        ]

    elif sent_post.photo:
        post_id = sent_post.message_id
        message_ids = [RelatedMessage(
            post_id=post_id,
            message_id=sent_post.message_id,
            photo_file_id=sent_post.photo[-1].file_id,
            photo_file_unique_id=sent_post.photo[-1].file_unique_id
        )]

    else:
        post_id = sent_post.message_id
        message_ids = []

    post_ad: PostAd = PostAd(
        post_id=post_id,
        post_type=state_class.lower(),
        user_id=obj.from_user.id,
        tag_category=ad.tag_category,
        tag_name=ad.tag_name,
        description=ad.description,
        price=ad.price,
        contacts=",".join(ad.contacts),
        currency_code=ad.currency_code,
        negotiable=ad.negotiable,
        related_messages=message_ids
    )

    session.add(post_ad)
    await session.commit()

    create_jobs(scheduler, obj.from_user.id, post_ad.post_id, config.tg_bot.channel_id)

    await call.answer("Объявление было успешно опубликовано в канале!")
    await manager.start(Main.main, mode=StartMode.RESET_STACK)
