from dataclasses import dataclass, field
from datetime import datetime

import pytz
from aiogram.utils.markdown import hitalic, hcode, hbold


@dataclass
class Ad:
    state_class: str

    state: str = ''

    heading: str = ""
    tag_category: str = ""
    tag_name: str = ""

    description: str = ""
    photos: dict | list = field(default_factory=dict)
    price: int = field(default_factory=int)
    contacts: list[str] = field(default_factory=list)

    currency_code: str = ""
    negotiable: bool = False
    mention: str = ""

    contact_limit: int = field(default=0)
    pic_limit: int = field(default=0)
    post_limit: int = field(default=0)

    post_link: str = ""
    updated_at: datetime = field(default=datetime.now(tz=pytz.timezone("Europe/Kiev")))
    created_at: datetime = field(default=datetime.now(tz=pytz.timezone("Europe/Kiev")))

    def to_text(self, where: str = None) -> str:
        description: str = self.description or '➖'
        price: float | int | str = self.price or '➖'
        contacts: str = self.contacts and self.humanize_phone_numbers() or '➖'

        if where == "edit" and self.pic_limit == 0:
            photos_len: str = "<code>Нет фото</code>"
        else:
            photos_len: str = self.photos and str(len(self.photos)) + ' шт' or '➖'

        if self.state_class in ("sell", "rent"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        tdescription = 'Описание товара или услуг'
        tphoto = 'Фото (опционально)'
        tcontact = 'Контактные данные'
        if self.state_class == "exchange":
            return (self.current_heading(where=where) +
                    f"1. {tdescription}: {hitalic(description)}\n"
                    f"2. {tphoto}: {photos_len}\n"
                    f"3. {tcontact}: {contacts}\n")
        else:
            if self.state_class in ("sell", "rent"):
                tprice = 'Цена'
            else:
                tprice = 'Желаемая цена (опционально)'

            return (self.current_heading(where=where) +
                    f"1. {tdescription}: {description}\n"
                    f"2. {tphoto}: {photos_len}\n"
                    f"3. {tprice}: {hbold(str(price)) + ' ' + (self.price and self.currency or '')} {self.price and negotiable or ''}\n"
                    f"4. {tcontact}: {contacts}\n")

    def current_heading(self, where: str = None) -> str:
        match self.state:
            case 'description':
                return '📝 Введите описание:\n\n'

            case 'price':
                if self.state_class in ("sell", "rent", "exchange"):
                    return '💸 Введите цену, так же укажите ' \
                               'валюту и уместен ли торг:\n\n'
                else:
                    return '💸 Введите цену, так же укажите ' \
                           'валюту:\n\n'

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
                elif not self.photos and self.state_class == "exchange":
                    return '📷 Отправьте фото товара или услуг которое вы хотите' \
                           ' обменять (этот раздел можно пропустить).\n' \
                           f'P.s. Максимальное количество картинок - <b>{self.pic_limit}</b>:\n\n'
                elif not self.photos:
                    return '📷 Отправьте фото ' \
                           'по одному (этот раздел можно пропустить).\n' \
                           f'P.s. Максимальное количество картинок - <b>{self.pic_limit}</b>:\n\n'
                else:
                    return '📷 Чтобы изменить картинку, просто отправьте ' \
                           'новую картинку, а чтобы удалить картинку нажми на ' \
                           'кнопку ниже.\n' \
                           f'P.s. Максимальное количество картинок - <b>{self.pic_limit}</b>:\n\n'

    def preview(self, where: str = None) -> str:
        preview_list: list[str] = [self.make_tags()]
        if self.state_class in ("sell", "rent"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        preview_list.append(f"Описание: {self.description}")

        if self.price and self.state_class in ("sell", "rent"):
            preview_list.append(f"Стоимость: {str(self.price) + ' ' + (self.price and self.currency or '')} "
                                f"{self.price and negotiable or ''}")
        elif self.price and self.state_class not in ("sell", "rent", "exchange"):
            preview_list.append(f"Желаемая цена: {str(self.price) + ' ' + self.currency}")

        preview_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")

        if self.photos:
            preview_list.append(f"Картинки: {len(self.photos)} шт")

        if where == "edit":
            stat_text: str = (f"Объявление: {self.post_link}\n"
                              f"{self.make_datetime_text()}")
            preview_list.append(stat_text)

        return '\n\n'.join(preview_list)

    def confirm(self) -> str:
        if self.state_class in ("sell", "rent"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        confirm_list: list[str] = [
            "Вы уверены что хотите опубликовать объявление"
            " со следующими данными?",
            f"Описание: {self.description}"
        ]
        if self.price and self.state_class not in ("sell", "rent"):
            confirm_list.append(f"Желаемая цена: {str(self.price) + ' ' + self.currency}")
        elif self.price:
            confirm_list.append(f"Цена: {str(self.price) + ' ' + (self.price and self.currency or '')} "
                                f"{self.price and negotiable or ''}",)
        confirm_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        if self.photos:
            confirm_list.append(f"Картинки: {len(self.photos)} шт")

        return '\n\n'.join(confirm_list)

    def post(self, where: str = None) -> str:
        if self.state_class in ("sell", "rent"):
            negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        else:
            negotiable: None = None

        post_list: list[str] = [
            self.make_tags(),
            f"{self.description}",

            f"Контактные данные: {self.humanize_phone_numbers()}",
            f"Телеграм: {self.mention}"
        ]

        if self.price and self.state_class in ("sell", "rent"):
            post_list.insert(2, f"Цена: {str(self.price) + ' ' + self.currency + ' ' + negotiable or ''}")
        elif self.price:
            post_list.insert(2, f"Желаемая цена: {str(self.price) + ' ' + self.currency}")

        if where == "admin_group":
            post_list.append(f"{self.make_datetime_text()}")
            post_list.insert(0, f"Объявление: {self.post_link}")

        return '\n\n'.join(post_list)

    def humanize_phone_numbers(self) -> str:
        return ", ".join(map(hitalic, self.contacts))

    def make_tags(self) -> str:
        headings: dict = {
            "buy": "Куплю",
            "sell": "Продам",
            "occupy": "Сниму",
            "rent": "Сдам",
            "exchange": "Обменяю"
        }
        heading = "#" + headings.get(self.state_class)
        category = "#" + headings.get(self.state_class) + self.tag_category
        tag = "#" + headings.get(self.state_class) + self.tag_category + self.tag_name
        return " ".join([heading, category, tag])

    def make_datetime_text(self) -> str:
        return f"Дата создания объявления: <code>{self.created_at.astimezone(pytz.timezone('Europe/Kiev')).strftime('%d.%m.%Y %H:%M:%S')}</code>\n" \
               f"Последнее обновление: <code>{self.updated_at.astimezone(pytz.timezone('Europe/Kiev')).strftime('%d.%m.%Y %H:%M:%S')}</code>"

    @property
    def currency(self):
        return {'USD': 'дол.', 'EUR': 'евро', 'RUB': 'руб.', 'UAH': 'грн.'}.get(self.currency_code, "руб.")
