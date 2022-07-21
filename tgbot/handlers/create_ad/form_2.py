# import copy
# from typing import Union, Dict, Any
#
# from aiogram import types
# from aiogram_dialog import DialogManager, ShowMode, Data, StartMode
# from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
# from aiogram_dialog.widgets.input import TextInput
# from aiogram_dialog.widgets.kbd import Button, Select, Row
# from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
# from aiogram_dialog.widgets.text import Format, Const
# from aiogram_dialog.widgets.when import Whenable
#
# from tgbot.config import Config
# from tgbot.misc.ad import Ad
# from tgbot.misc.states import Sell, Buy, Preview, ConfirmAd, Main, ShowMyAd, EditSell, EditBuy
# from tgbot.models.post_ad import PostAd
# from tgbot.services.db_commands import DBCommands
#
# REQUIRED_FIELDS = {
#     "sell": {"description", "price", "contacts", "tags"},
#     "buy": {"description", "contacts", "tags"},
# }
#
# to_state: dict = {
#     "sell": Sell,
#     "buy": Buy,
#     "editsell": EditSell,
#     "editbuy": EditBuy
# }
#
#
# def get_active_section(state: str):
#     sections = {
#         'title': 'Заголовок',
#         'description': 'Описание',
#         'price': 'Цена',
#         'contact': 'Контакты',
#         'photo': 'Картинка',
#         'tags': 'Теги'
#     }
#     return sections.get(state)
#
#
# def when_not(key: str):
#     def f(data, _whenable, _manager):
#         return not data.get(key)
#
#     return f
#
#
# def get_current_file_id(photos: list[str] = None, page: int | None = None) -> None | str:
#     if not all([photos, page]):
#         return None
#     else:
#         return photos[page - 1]
#
#
# async def on_back(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     start_data = manager.current_context().start_data
#     items_to_pop = ['state_class', 'current_page', 'photos_len']
#     for item in items_to_pop:
#         start_data.pop(item, None)
#
#     await manager.done(start_data)
#
#
# async def change_photo(_call: types.CallbackQuery, button: Button, manager: DialogManager):
#     data = manager.current_context().start_data
#     current_page: int = data.get('current_page')
#     photos_len: int = data.get('photos_len')
#
#     action: str = button.widget_id
#
#     if action == 'left_photo':
#         current_page -= 1
#         if current_page < 1:
#             current_page = photos_len
#     elif action == 'right_photo':
#         current_page += 1
#         if current_page > photos_len:
#             current_page = 1
#
#     data['current_page'] = current_page
#
#
# async def change_page(_obj: Union[types.CallbackQuery, types.Message], button: Union[Button, TextInput],
#                       manager: DialogManager, *_text):
#     action: str = button.widget_id
#     current_state = manager.current_context().state.state.split(":")[-1]
#     states_group = manager.current_context().state.state.split(":")[0].lower()
#
#     if action == 'left':
#         if current_state == 'tags':
#             await manager.dialog().switch_to(to_state.get(states_group).contact)
#         else:
#             await manager.dialog().back()
#     elif action == 'right':
#         if current_state == 'contact':
#             await manager.dialog().switch_to(to_state.get(states_group).tags)
#         else:
#             await manager.dialog().next()
#     elif current_state != 'contact':
#         await manager.dialog().next()
#
#
# async def add_tag(_call: types.CallbackQuery, _widget: ManagedWidgetAdapter[Select], manager: DialogManager,
#                   tag: str):
#     tag_limit: int = manager.current_context().widget_data.get('tag_limit')
#     tags_data = manager.current_context().widget_data.setdefault("tags", [])
#     tags_data.append(tag.removeprefix('#️⃣'))
#     if tag_limit == len(tags_data):
#         await manager.dialog().next()
#
#
# async def currency_selected(_call: types.CallbackQuery, _widget: Any, manager: DialogManager, item_id: str):
#     currencies = {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}
#     manager.current_context().widget_data['currency'] = currencies[item_id]
#
#
# async def delete_tag(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     manager.current_context().widget_data.get("tags").pop()
#
#
# async def delete_contact(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     manager.current_context().widget_data.get("contacts").pop()
#
#
# async def delete_pic(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     manager.current_context().widget_data.get("photos_ids").pop()
#
#
# def tag_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
#     tags: list = manager.current_context().widget_data.get('tags')
#     return tags is not None and len(tags) > 0
#
#
# def contact_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
#     contacts: list = manager.current_context().widget_data.get('contacts')
#     return contacts is not None and len(contacts) > 0
#
#
# def pic_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
#     photos_ids: list = manager.current_context().widget_data.get('photos_ids')
#     return photos_ids is not None and len(photos_ids) > 0
#
#
# # Restrictions
# def fixed_size_64(text: str):
#     if len(text) > 128:
#         raise ValueError
#
#
# def fixed_size_1024(text: str):
#     if len(text) > 1024:
#         raise ValueError
#
#
# async def invalid_input(message: types.Message, _widget: TextInput, manager: DialogManager):
#     state = manager.current_context().state
#     manager.show_mode = ShowMode.EDIT
#     match state:
#         case Sell.title | Buy.title:
#             await message.answer("Максимальная длина заголовка товара или услуг 64 символов."
#                                  " Попробуйте еще раз.")
#         case Sell.description | Buy.description:
#             await message.answer("Максимальная длина описания товара или услуг 128 символов."
#                                  " Попробуйте еще раз.")
#
#
# async def price_validator(message: types.Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
#     try:
#         price: float = (float(message.text).is_integer() and int(message.text)) or round(float(message.text), 2)
#
#         if not (price > 0.01):
#             raise ValueError
#
#         manager.current_context().widget_data["price"] = price
#         await dialog.next()
#     except ValueError:
#         manager.show_mode = ShowMode.EDIT
#         await message.answer("Цена должна быть числом и быть больше 0.01. Попробуйте еще раз.")
#
#
# class RepeatedNumberError(Exception):
#     pass
#
#
# async def contact_validator(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
#     contact_limit: int = manager.current_context().widget_data.get('contact_limit')
#     try:
#         phone_number = message.text.replace(' ', '')
#
#         if phone_number.startswith('+'):
#             phone_number.removeprefix('+')
#         if not phone_number.isdigit():
#             raise ValueError
#
#         phone_number = '+' + phone_number
#         contact_data = manager.current_context().widget_data.setdefault('contacts', [])
#
#         if phone_number in contact_data:
#             raise RepeatedNumberError
#         if len(contact_data) < contact_limit:
#             contact_data.append(phone_number)
#         else:
#             contact_data[-1] = phone_number
#     except ValueError:
#         manager.show_mode = ShowMode.EDIT
#         await message.answer("Вы ввели неверный формат номера телефона. Попробуйте еще раз.")
#     except RepeatedNumberError:
#         manager.show_mode = ShowMode.EDIT
#         await message.answer("Вы уже ввели этот номер.")
#
#
# async def pic_validator(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
#     pic_limit: int = manager.current_context().widget_data.get('pic_limit')
#     if pic_limit == 0:
#         return []
#
#     match message.content_type:
#         case types.ContentType.PHOTO:
#
#             photo = message.photo[-1]
#             photos_data = manager.current_context().widget_data.setdefault('photos_ids', [])
#             photos_unique_ids = manager.current_context().widget_data.setdefault('photos_unique_ids', [])
#
#             if photo.file_unique_id in photos_unique_ids:
#                 manager.show_mode = ShowMode.EDIT
#                 await message.answer("Эта картинка уже имеется в объявление. Отправьте другое.")
#                 return
#
#             if len(photos_data) < pic_limit:
#                 photos_data.append(photo.file_id)
#                 photos_unique_ids.append(photo.file_unique_id)
#             else:
#                 photos_data[-1] = photo.file_id
#                 photos_unique_ids[-1] = photo.file_unique_id
#
#         case _:
#             manager.show_mode = ShowMode.EDIT
#             await message.answer("Вы ввели не валидную картинку! Попробуйте еще раз.")
#
#
# # Buttons and dialogs
# async def set_default(_, dialog_manager: DialogManager):
#     await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id="UAH")
#
#
# async def set_edit_default(_, dialog_manager: DialogManager):
#     session = dialog_manager.data.get('session')
#     db: DBCommands = dialog_manager.data.get('db_commands')
#
#     post_ad: PostAd = await session.get(PostAd, int(dialog_manager.current_context().start_data.get('post_id')))
#
#     tag, contact, pic, post = await db.get_values_of_restrictions()
#     limits: dict = {
#         "tag_limit": tag,
#         "contact_limit": contact,
#         "pic_limit": len(post_ad.related_messages) if post_ad.related_messages else 0,
#         "post_limit": post
#     }
#
#     dialog_manager.current_context().widget_data['post_id'] = post_ad.post_id
#     dialog_manager.current_context().widget_data['tags'] = [tag.tag_name for tag in post_ad.tags]
#     dialog_manager.current_context().widget_data['contacts'] = post_ad.contacts.split(',') if post_ad.contacts else []
#     if post_ad.related_messages:
#         photos_ids = [m.photo_file_id for m in post_ad.related_messages]
#     else:
#         photos_ids = []
#     dialog_manager.current_context().widget_data['photos_ids'] = photos_ids
#     dialog_manager.current_context().widget_data.update(limits)
#
#     # ToDo deal with bug with checkbox
#     await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id=post_ad.currency_code)
#     await dialog_manager.dialog().find('negotiable').set_checked(event=dialog_manager.event, checked=post_ad.negotiable)
#
#
# async def get_currency_data(**_kwargs):
#     currencies = [
#         ('$', 'USD'),
#         ('€', 'EUR'),
#         ('₽', 'RUB'),
#         ('₴', 'UAH')
#     ]
#     return {'currencies': currencies}
#
#
# async def check_required_fields(call: types.CallbackQuery, button: Button, manager: DialogManager):
#     widget_data: dict = manager.current_context().widget_data
#
#     if button.widget_id == 'post':
#         state_class = manager.current_context().state.state.split(':')[0]
#         if REQUIRED_FIELDS.get(state_class.lower()).issubset(widget_data.keys()):
#
#             data: dict = copy.deepcopy(widget_data)
#             data.pop('sg_tags', None)
#             data.update({"state_class": state_class})
#             await manager.start(ConfirmAd.confirm, data=data)
#
#         else:
#             await call.answer("Вы не заполнили все обязательные поля.")
#     else:
#         start_data = manager.current_context().start_data
#         obj = manager.event
#         db: DBCommands = manager.data.get("db_commands")
#         session = manager.data.get("session")
#         config: Config = manager.data.get("config")
#
#         post_id = int(start_data.get("post_id"))
#         post_ad: PostAd = await session.get(PostAd, post_id)
#         print("widget_data", widget_data)
#         items_to_pop = ['post_id', 'currency', 'sg_tags', 'state_class', 'tag_limit', 'contact_limit', 'pic_limit', 'post_limit']
#         for item in items_to_pop:
#             widget_data.pop(item, None)
#
#         await update_ad(post_ad, widget_data, db)
#
#         data: dict = {
#             "state_class": post_ad.post_type.capitalize(),
#             "tags": [tag.tag_name for tag in post_ad.tags],
#             "description": post_ad.description,
#             "contacts": post_ad.contacts.split(",") if post_ad.contacts else [],
#             "price": post_ad.price,
#             "currency_code": post_ad.currency_code,
#             "negotiable": post_ad.negotiable,
#             "title": post_ad.title,
#             "photos_ids": [m.photo_file_id for m in post_ad.related_messages] if post_ad.related_messages else [],
#             "mention": obj.from_user.get_mention()
#         }
#
#         ad: Ad = Ad(**data)
#
#         if post_ad.related_messages:
#             print("_______________________")
#             for m in post_ad.related_messages:
#                 print(m.message_id, m.photo_file_id)
#             for k in post_ad.photos_ids.split(",")[:-1]:
#                 print(k)
#             print(post_ad.related_messages)
#             print(post_ad.photos_ids.split(","))
#             await call.message.answer_photo(post_ad.photos_ids.split(",")[-1])
#             print("_______________________")
#         else:
#             await call.bot.edit_message_text(
#                 chat_id=config.tg_bot.channel_id,
#                 message_id=post_ad.post_id,
#                 text=ad.post()
#             )
#
#         #     post_id_photo_id = itertools.zip_longest(post_ad.related_messages, post_ad.photos_ids.split(","))
#         #     for message, photo_id in post_id_photo_id:
#         #         if photo_id:
#         #             await call.bot.edit_message_media(
#         #                 chat_id=config.tg_bot.channel_id,
#         #                 message_id=message.message_id,
#         #                 media=types.InputMedia(media=photo_id)
#         #             )
#         #         else:
#         #             await call.bot.delete_message(
#         #                 chat_id=config.tg_bot.channel_id,
#         #                 message_id=message.message_id
#         #             )
#         #             await session.delete(message)
#         #
#         # data: dict = {
#         #     "state_class": post_ad.post_type.capitalize(),
#         #     "tags": [tag.tag_name for tag in post_ad.tags],
#         #     "description": post_ad.description,
#         #     "contacts": post_ad.contacts.split(",") if post_ad.contacts else [],
#         #     "price": post_ad.price,
#         #     "currency_code": post_ad.currency_code,
#         #     "negotiable": post_ad.negotiable,
#         #     "title": post_ad.title,
#         #     "photos_ids": post_ad.photos_ids.split(",") if post_ad.photos_ids else [],
#         #     "mention": obj.from_user.get_mention()
#         # }
#         #
#         # ad: Ad = Ad(**data)
#         #
#         # await call.bot.edit_message_caption(
#         #     chat_id=config.tg_bot.channel_id,
#         #     message_id=post_ad.post_id,
#         #     caption=ad.post()
#         # )
#         #
#         # await session.commit()
#         await call.answer("Объявление обновлено!")
#         await manager.start(state=ShowMyAd.true, data={"post_id": post_id}, mode=StartMode.RESET_STACK)
#
#
# async def update_ad(post_ad: PostAd, dict_to_update: dict, db: DBCommands):
#     if dict_to_update.get("tags") is not None:
#         post_ad.tags = await db.get_tags_by_name(dict_to_update["tags"])
#     if dict_to_update.get("description") is not None:
#         post_ad.description = dict_to_update["description"]
#     if dict_to_update.get("contacts") is not None:
#         post_ad.contacts = ','.join(dict_to_update["contacts"])
#     if dict_to_update.get("price") is not None:
#         post_ad.price = dict_to_update["price"]
#     if dict_to_update.get("currency_code") is not None:
#         post_ad.currency_code = dict_to_update["currency_code"]
#     if dict_to_update.get("negotiable") is not None:
#         post_ad.negotiable = dict_to_update["negotiable"]
#     if dict_to_update.get("title") is not None:
#         post_ad.title = dict_to_update["title"]
#     if dict_to_update.get("photos_ids") is not None:
#         post_ad.photos_ids = ','.join(dict_to_update["photos_ids"])
#
#
# async def show_preview(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     state_class = manager.current_context().state.state.split(":")[0]
#     widget_data: dict = manager.current_context().widget_data
#     data: dict = copy.deepcopy(widget_data)
#     data.pop('currency_code', None)
#     data.pop('sg_tags', None)
#     data.update({"state_class": state_class})
#
#     await manager.start(state=Preview.preview, data=data)
#
#
# async def process_result(_start_data: Data, result: Any, manager: DialogManager):
#     if result:
#         manager.current_context().widget_data.update(**result)
#
#
# def get_widgets(where: str = "main"):
#     if where == 'edit':
#         btn = "Сохранить"
#         btn_id = "save"
#     else:
#         btn = "Опубликовать"
#         btn_id = "post"
#     buttons = (
#         Format(text="{form_text}", when="form_text"),
#         Row(
#             Button(text=Const("<<"), id="left", on_click=change_page),
#             Button(text=Format(text="{page}"), id="page"),
#             Button(text=Const(">>"), id="right", on_click=change_page)
#         ),
#         Row(
#             Button(
#                 text=Const("🔚 Назад"),
#                 id=f"go_back_{where}",
#                 on_click=go_back_page
#             ),
#             Button(
#                 text=Const("👁"),
#                 id="preview",
#                 on_click=show_preview
#             ),
#             Button(
#                 text=Const(btn),
#                 id=btn_id,
#                 on_click=check_required_fields
#             )
#         )
#     )
#     return buttons
#
#
# async def go_back_page(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     state = manager.current_context().state.state.split(":")[0]
#     if state == "EditSell":
#         start_data = manager.current_context().start_data
#         await manager.start(state=ShowMyAd.true, data=start_data, mode=StartMode.RESET_STACK)
#     else:
#         await manager.start(state=Main.main, mode=StartMode.RESET_STACK)
#
#
# def make_link_to_post(channel_id: int, post_id: int):
#     return f"https://t.me/c/{str(channel_id).removeprefix('-100')}/{post_id}"
