from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from aiogram.utils.markdown import hunderline, hbold, hitalic, hcode

from tgbot.constants import ACTIVE, INACTIVE, REJECTED


@dataclass
class Ad:
    state_class: str

    status: Optional[str] = None
    state: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    title: str = ""
    photos_ids: list[str] = field(default_factory=list)
    photos_unique_ids: list[str] = field(default_factory=list)
    description: str = ""
    price: float | int = field(default_factory=float)
    contacts: list[str] = field(default_factory=list)

    currency_code: str = ""
    negotiable: bool = False
    mention: str = ""

    tag_limit: int = field(default=0)
    contact_limit: int = field(default=0)
    pic_limit: int = field(default=0)
    post_limit: int = field(default=0)

    post_link: str = ""
    updated_at: datetime = field(default=datetime.today())
    created_at: datetime = field(default=datetime.today())

    def to_text(self, where: str = None) -> str:
        title: str = self.title or '➖'
        description: str = self.description or '➖'
        price: float | int | str = self.price or '➖'
        contacts: str = self.contacts and self.humanize_phone_numbers() or '➖'

        if where == "edit" and self.pic_limit == 0:
            photos_len: str = "<code>Нет фото</code>"
        else:
            photos_len: str = self.photos_ids and str(len(self.photos_ids)) + ' шт' or '➖'

        if self.state_class in ("Sell", "EditSell"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        ttags = self.state == 'tags' and hunderline('Теги') or 'Теги'
        ttitle = self.state == 'title' and hunderline('Заголовок товара или услуг (опционально)') \
                 or 'Заголовок товара или услуг (опционально)'
        tdescription = self.state == 'description' and hunderline(
            'Описание товара или услуг') or 'Описание товара или услуг'
        tphoto = self.state == 'photo' and \
                 hunderline('Фото (опционально)') or 'Фото (опционально)'
        tcontact = self.state == 'contact' and hunderline('Контактные данные') \
                   or 'Контактные данные'
        if self.state_class in ("Sell", "EditSell"):
            tprice = self.state == 'price' and hunderline('Цена') or 'Цена'
        else:
            tprice = self.state == 'price' and hunderline(
                'Желаемая цена (опционально)') or 'Желаемая цена (опционально)'

        return (self.current_heading(where=where) +
                f"1. {ttags}: {self.make_tags()}\n"
                f"2. {ttitle}: {hbold(title)}\n"
                f"3. {tdescription}: {hitalic(description)}\n"
                f"4. {tphoto}: {photos_len}\n"
                f"5. {tprice}: {hcode(str(price) + ' ' + (self.price and self.currency or ''))} {self.price and negotiable or ''}\n"
                f"6. {tcontact}: {contacts}\n")

    def current_heading(self, where: str = None) -> str:
        match self.state:
            case "tags":
                if not self.tags and self.state_class == "Sell":
                    return '#️⃣  Выберите тег своего товара или услуг нажав по кнопке ' \
                           f'ниже (макс. <code>{self.tag_limit}</code>):\n\n'
                elif not self.tags and self.state_class == "Buy":
                    return '#️⃣  Выберите тег товара или услуг который вы хотите ' \
                           f'купить нажав по кнопке ниже (макс. <code>{self.tag_limit}</code>):\n\n'
                else:
                    return '#️⃣  Чтобы удалить тег нажмите на кнопку удалить тег ниже' \
                           f'(макс. <code>{self.tag_limit}</code>).\n\n'

            case 'title':
                if not self.title and self.state_class == "Sell":
                    return '🔡 Введите заголовок товара или услуг (этот раздел можно пропустить):\n\n'
                elif not self.title and self.state_class == "Buy":
                    return '🔡 Введите заголовок товара или услуг который вы хотите купить ' \
                           '(этот раздел можно пропустить):\n\n'
                else:
                    return '🔡 Чтобы изменить заголовок товара или услуг, просто отправьте' \
                           ' новое название.\n\n'

            case 'description':
                if not self.description and self.state_class == "Sell":
                    return '📝 Введите описание товара или услуг:\n\n'
                elif not self.description and self.state_class == "Buy":
                    return '📝 Введите описание товара или услуг которое ' \
                           'вы хотите купить:\n\n'
                else:
                    return '📝 Чтобы изменить описание товара или услуг, просто отправьте ' \
                           'новое описание.\n\n'

            case 'price':
                if not self.price and self.state_class == "Sell":
                    return '💸 Введите цену товара или услуг, так же укажите ' \
                           'валюту и уместен ли торг:\n\n'
                elif not self.price and self.state_class == "Buy":
                    return '💸 Введите желаемую цену товара или услуг и укажите ' \
                           'валюту:\n\n'
                else:
                    return '💸 Чтобы изменить цену товара или услуг, просто отправьте ' \
                           'новую цену.\n\n'

            case 'contact':
                if not self.contacts:
                    return '📞 Введите номер телефона который будет отображаться в объявлении ' \
                           f'(макс. <code>{self.contact_limit}</code>):\n\n'
                else:
                    return '📞 Чтобы изменить номер телефона, просто' \
                           ' отправьте новый номер, а чтобы удалить нажмите на кнопку удалить контакт ' \
                           f'(макс. <code>{self.contact_limit}</code>).\n\n'

            case _:
                if where == "edit" and self.pic_limit == 0:
                    return '⛔️ Так как при создании объявления вы не добавляли фотки ' \
                           'вашего товара или услуг вы не можете добавить фотки при ' \
                           'изменении. Чтобы добавить фотки создайте новое ' \
                           'объявление.\n\n'
                elif not self.photos_ids and self.state_class == "Sell":
                    return '📷 Отправьте картинки товара или услуг по одному ' \
                           '(этот раздел можно пропустить).\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'
                elif not self.photos_ids:
                    return '📷 Отправьте картинки товара или услуг который вы хотите купить ' \
                           'по одному (этот раздел можно пропустить).\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'
                else:
                    return '📷 Чтобы изменить картинку товара или услуг, просто отправьте ' \
                           'новую картинку, а чтобы удалить картинку нажми на ' \
                           'кнопку ниже.\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'

    def preview(self, where: str = None) -> str:
        preview_list: list[str] = []
        if self.state_class in ("Sell", "EditSell"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        if self.tags:
            preview_list.append(("Теги: " + self.make_tags()))
        else:
            preview_list.append('Теги не указаны ❗️')

        if self.title:
            preview_list.append(f"Заголовок: {hbold(self.title)}")

        if self.description:
            preview_list.append(f"Описание: {hitalic(self.description)}")
        else:
            preview_list.append("Описание отсутствует ❗️")

        if self.price and self.state_class in ("Sell", "EditSell"):
            preview_list.append(f"Стоимость: {hcode(str(self.price) + ' ' + (self.price and self.currency or ''))} "
                                f"{self.price and negotiable or ''}")
        elif not self.price and self.state_class in ("Sell", "EditSell"):
            preview_list.append("Цена не указана ❗️")
        elif self.price and self.state_class not in ("Sell", "EditSell"):
            preview_list.append(f"Желаемая цена: {hcode(str(self.price) + ' ' + self.currency)}")

        if self.contacts:
            preview_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        else:
            preview_list.append("Контактные данные не указаны ❗️")

        if self.photos_ids:
            preview_list.append(f"Картинки: {len(self.photos_ids)} шт")

        if where == "edit":
            stat_text: str = (f"Объявление: {self.post_link}\n"
                              f"Статус объявления: {self.get_status()}\n"
                              f"{self.make_datetime_text()}")
            preview_list.append(stat_text)

        return '\n\n'.join(preview_list)

    def confirm(self) -> str:
        if self.state_class in ("Sell", "EditSell"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        confirm_list: list[str] = [
            "Вы уверены что хотите опубликовать пост об объявлении"
            " со следующими данными?",
            f"Теги: {self.make_tags(self.state_class)}",
            f"Описание: {hitalic(self.description)}"
        ]
        if self.price and self.state_class not in ("Sell", "EditSell"):
            confirm_list.append(f"Желаемая цена: {hcode(str(self.price) + ' ' + self.currency)}")
        else:
            confirm_list.append(f"Цена: {hcode(str(self.price) + ' ' + (self.price and self.currency or ''))} "
                                f"{self.price and negotiable or ''}",)
        confirm_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        if self.title:
            confirm_list.insert(2, f"Заголовок: {hbold(self.title)}")
        if self.photos_ids:
            confirm_list.append(f"Картинки: {len(self.photos_ids)} шт")

        return '\n\n'.join(confirm_list)

    def post(self) -> str:
        if self.state_class in ("Sell", "EditSell"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        post_list: list[str] = [
            self.make_tags(self.state_class),
            f"{hitalic(self.description)}",

            f"Контактные данные: {self.humanize_phone_numbers()}",
            f"Телеграм: {self.mention}"
        ]

        if self.title:
            post_list.insert(1, f"{hbold(self.title)}")
        if self.price:
            post_list.insert(-2, f"{hcode(str(self.price) + ' ' + self.currency) + ' ' + negotiable or ''}")

        return '\n\n'.join(post_list)

    def humanize_phone_numbers(self) -> str:
        list_of_numbers: list[str] = list()
        for number in self.contacts:
            if not number.startswith('+'):
                number = '+' + number
            list_of_numbers.append(hcode(number))

        return ", ".join(list_of_numbers)

    def make_tags(self, state_class: str = None) -> str:
        print(state_class)
        tags = self.tags
        if state_class:
            tags.insert(0, "продам" if state_class == "Sell" else "куплю")
        return ", ".join(["#" + tag for tag in tags])

    def make_datetime_text(self) -> str:
        return f"Дата создания объявления: <code>{self.created_at.strftime('%d.%m.%Y %H:%M:%S')}</code>\n" \
               f"Последнее обновление: <code>{self.updated_at.strftime('%d.%m.%Y %H:%M:%S')}</code>"

    def get_status(self) -> str:
        status: dict = {
            ACTIVE: "Активное ✅",
            INACTIVE: "Неактивное ❌",
            REJECTED: "Отклонено ⚠️"
        }
        return status.get(self.status, "Не определено")

    @property
    def currency(self):
        return {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}.get(self.currency_code, "₴")


# @dataclass
# class SalesAd(Ad):
#     def to_text(self, where: str = None) -> str:
#
#
#     def current_heading(self, where: str = None) -> str:
#
#     def preview(self, where: str = None) -> str:
#
#
#     def confirm(self, state_class: str = None) -> str:
#
#
#     def post(self) -> str:
#
#
#
# class PurchaseAd(Ad):
#     def to_text(self, where: str = None) -> str:
#         description: str = self.description or '➖'
#         title: str = self.title or '➖'
#         photos_len: str = self.photos_ids and str(len(self.photos_ids)) + ' шт' or '➖'
#         contacts: str = self.contacts and self.humanize_phone_numbers() or '➖'
#         price: float | int | str = self.price or '➖'
#
#         ttags = self.state == 'tags' and hunderline('Теги') or 'Теги'
#         ttitle = self.state == 'title' and hunderline('Заголовок товара или услуг (опционально)') \
#                  or 'Заголовок товара или услуг (опционально)'
#         tdescription = self.state == 'description' and hunderline(
#             'Описание товара или услуг') or 'Описание товара или услуг'
#         tphoto = self.state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'
#         tcontact = self.state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'
#         tprice = self.state == 'price' and hunderline('Желаемая цена (опционально)') or 'Желаемая цена (опционально)'
#
#         return (self.current_heading() +
#                 f"1. {ttags}: {self.make_tags()}\n"
#                 f"2. {ttitle}: {hbold(title)}\n"
#                 f"3. {tdescription}: {hitalic(description)}\n"
#                 f"4. {tphoto}: {photos_len}\n"
#                 f"5. {tprice}: {hcode(str(price) + ' ' + (self.price and self.currency or ''))}\n"
#                 f"6. {tcontact}: {contacts}\n")
#
#     def current_heading(self, where: str = None) -> str:
#         match self.state:
#             case "tags":
#                 if not self.tags:
#                     return '#️⃣  Выберите тег товара или услуг который вы хотите ' \
#                            f'купить нажав по кнопке ниже (макс. <code>{self.tag_limit}</code>):\n\n'
#                 else:
#                     return '#️⃣  Чтобы изменить тег, сначала удалите текущий ' \
#                            f'тег, затем установите новый (макс. <code>{self.tag_limit}</code>).\n\n'
#
#             case 'title':
#                 if not self.title:
#                     return '🔡 Введите заголовок товара или услуг который вы хотите купить ' \
#                            '(этот раздел можно пропустить):\n\n'
#                 else:
#                     return '🔡 Чтобы изменить заголовок товара или услуг, просто отправьте ' \
#                            'новое название.\n\n'
#
#             case 'description':
#                 if not self.description:
#                     return '📝 Введите описание товара или услуг которое ' \
#                            'вы хотите купить:\n\n'
#                 else:
#                     return '📝 Чтобы изменить описание, просто отправьте ' \
#                            'новое описание.\n\n'
#
#             case 'price':
#                 if not self.price:
#                     return '💸 Введите желаемую цену товара или услуг и укажите ' \
#                            'валюту:\n\n'
#                 else:
#                     return '💸 Чтобы изменить желаемую цену товара или услуг, просто отправьте ' \
#                            'новую цену (этот раздел можно пропустить).\n\n'
#
#             case 'contact':
#                 if not self.contacts:
#                     return '📞 Введите номер телефона который будет отображаться в объявлении ' \
#                            f'(макс. <code>{self.contact_limit}</code>):\n\n'
#                 else:
#                     return '📞 Чтобы изменить номер телефона, просто отправьте ' \
#                            f'отправьте новый номер (макс. <code>{self.contact_limit}</code>).\n\n'
#
#             case _:
#                 if not self.photos_ids:
#                     return '🖼 Отправьте картинки товара или услуг который вы хотите купить ' \
#                            'по одному (этот раздел можно пропустить).\n' \
#                            f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'
#                 else:
#                     return '🖼 Чтобы изменить картинку товара или услуг, просто отправьте ' \
#                            'новую картинку, а чтобы удалить картинку нажми на ' \
#                            'кнопку ниже.\n' \
#                            f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>'
#
#     def preview(self, where: str = None) -> str:
#         preview_list: list[str] = []
#
#         if self.tags:
#             preview_list.append(self.make_tags())
#         else:
#             preview_list.append('Теги не указаны ❗️')
#
#         if self.title:
#             preview_list.append(f"Куплю {hbold(self.title)}")
#
#         if self.description:
#             preview_list.append(f"{hitalic(self.description)}")
#         else:
#             preview_list.append("Описание отсутствует ❗️")
#
#         if self.price:
#             preview_list.append(f"Желаемая цена: {hcode(str(self.price) + ' ' + self.currency)}")
#
#         if self.contacts:
#             preview_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
#         else:
#             preview_list.append("Контактные данные не указаны ❗️")
#
#         if self.photos_ids:
#             preview_list.append(f"Картинки: {len(self.photos_ids)} шт")
#
#         if where == "edit":
#             stat_text: str = (f"Объявление: {self.post_link}\n"
#                               f"Статус объявления: {self.get_status()}\n"
#                               f"{self.make_datetime_text()}")
#             preview_list.append(stat_text)
#
#         return '\n\n'.join(preview_list)
#
#     def confirm(self, state_class: str = None) -> str:
#         confirm_list: list[str] = [
#             "Вы уверены что хотите опубликовать пост об объявлении"
#             " со следующими данными?",
#             f"Теги: {self.make_tags(state_class)}",
#             f"Описание: {hitalic(self.description)}"
#         ]
#
#         if self.price:
#             confirm_list.append(f"Желаемая цена: {hcode(str(self.price) + ' ' + self.currency)}")
#
#         confirm_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
#
#         if self.title:
#             confirm_list.append(f"Заголовок: {hbold(self.title)}")
#         if self.photos_ids:
#             confirm_list.append(f"Картинки: {len(self.photos_ids)} шт")
#
#         return '\n\n'.join(confirm_list)
#
#     def post(self) -> str:
#         post_list: list[str] = [
#             self.make_tags()
#         ]
#
#         if self.title:
#             post_list.append(f"Куплю {hbold(self.title)}")
#
#         post_list.append(f"{hitalic(self.description)}")
#         if self.price:
#             post_list.append(f"{hcode(str(self.price) + ' ' + self.currency)}")
#         post_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
#         post_list.append(f"Телеграм: {self.mention}")
#         return '\n\n'.join(post_list)
