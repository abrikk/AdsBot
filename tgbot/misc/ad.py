from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import flag
import phonenumbers
from aiogram.utils.markdown import hunderline, hbold, hitalic, hcode


@dataclass
class Ad(ABC):
    state: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    description: str = field(default_factory=str)
    price: float | int = field(default_factory=float)
    contacts: list[str] = field(default_factory=list)
    title: str = field(default_factory=str)
    photos_ids: list[str] = field(default_factory=list)

    currency_code: str = field(default_factory=str)
    currency: str = {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}.get(currency_code, "₴")
    mention: str = field(default_factory=str)

    tag_limit: int = field(default_factory=int)
    contact_limit: int = field(default_factory=int)
    pic_limit: int = field(default_factory=int)
    post_limit: int = field(default_factory=int)

    @abstractmethod
    def to_text(self):
        pass

    @abstractmethod
    def current_heading(self) -> str:
        pass

    @abstractmethod
    def preview(self) -> str:
        pass

    @abstractmethod
    def confirm(self) -> str:
        pass

    @abstractmethod
    def post(self) -> str:
        pass

    def humanize_phone_numbers(self) -> str:
        list_of_numbers: list[str] = list()
        for number in self.contacts:
            if not number.startswith('+'):
                number = '+' + number
            number = phonenumbers.parse(number)
            emoji = ' ' + flag.flag(f"{phonenumbers.region_code_for_country_code(number.country_code)}")
            list_of_numbers.append(
                hcode(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)) + emoji)

        return ", ".join(list_of_numbers)

    def make_tags(self) -> str:
        return ", ".join(["#" + tag for tag in self.tags])


@dataclass
class SalesAd(Ad):
    negotiable: bool = False

    def to_text(self) -> str:
        description: str = self.description or '➖'
        price: float | int | str = self.price or '➖'
        negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        contacts: str = self.contacts and self.humanize_phone_numbers() or '➖'

        title: str = self.title or '➖'
        photos_len: str = self.photos_ids and str(len(self.photos_ids)) + ' шт' or '➖'

        ttags = self.state == 'tags' and hunderline('Теги') or 'Теги'
        tdescription = self.state == 'description' and hunderline(
            'Описание товара или услуг') or 'Описание товара или услуг'
        tprice = self.state == 'price' and hunderline('Цена') or 'Цена'
        tcontact = self.state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'
        ttitle = self.state == 'title' and hunderline('Заголовок товара или услуг (опционально)') \
                 or 'Заголовок товара или услуг (опционально)'
        tphoto = self.state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'

        return (self.current_heading() +
                f"1. {ttags}: {self.make_tags()}\n"
                f"2. {tdescription}: {hitalic(description)}\n"
                f"3. {tprice}: {hcode(str(price) + ' ' + (self.price and self.currency or ''))} {self.price and negotiable or ''}\n"
                f"4. {tcontact}: {contacts}\n"
                f"5. {ttitle}: {hbold(title)}\n"
                f"6. {tphoto}: {photos_len}\n")

    def current_heading(self) -> str:
        match self.state:
            case "tags":
                if not self.tags:
                    return '#️⃣  Выберите тег своего товара или услуг нажав по кнопке ' \
                           f'ниже (макс. <code>{self.tag_limit}</code>):\n\n'
                else:
                    return '#️⃣  Чтобы удалить тег нажмите на кнопку удалить тег ниже' \
                           f'(макс. <code>{self.tag_limit}</code>).\n\n'

            case 'description':
                if not self.description:
                    return '📝 Введите описание товара или услуг:\n\n'
                else:
                    return '📝 Чтобы изменить описание товара или услуг, просто отправьте ' \
                           'новое описание.\n\n'

            case 'price':
                if not self.price:
                    return '💸 Введите цену товара или услуг, так же укажите ' \
                           'валюту и уместен ли торг:\n\n'
                else:
                    return '💸 Чтобы изменить цену товара или услуг, просто отправьте ' \
                           'новую цену.\n\n'

            case 'contact':
                if not self.contacts:
                    return '📞 Введите номер телефона который будет отображаться в объявлении ' \
                           f'(макс. <code>{self.contact_limit}</code>):\n\n'
                else:
                    return '📞 Чтобы изменить номер телефона, просто отправьте' \
                           ' отправьте новый номер, а чтобы удалить нажмите на кнопку удалить контакт ' \
                           f'(макс. <code>{self.contact_limit}</code>).\n\n'

            case 'title':
                if not self.title:
                    return '🔡 Введите заголовок товара или услуг (этот раздел можно пропустить):\n\n'
                else:
                    return '🔡 Чтобы изменить заголовок товара или услуг, просто отправьте' \
                           ' новое название.\n\n'

            case _:
                if not self.photos_ids:
                    return '🖼 Отправьте картинки товара или услуг по одному ' \
                           '(этот раздел можно пропустить).\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'
                else:
                    return '🖼 Чтобы изменить картинку товара или услуг, просто отправьте ' \
                           'новую картинку, а чтобы удалить картинку нажми на ' \
                           'кнопку ниже.\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'

    def preview(self) -> str:
        preview_list: list[str] = []
        negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'

        if self.tags:
            preview_list.append(self.make_tags())
        else:
            preview_list.append('Теги не указаны ❗️')

        if self.title:
            preview_list.append(f"Продается {hbold(self.title)}")

        if self.description:
            preview_list.append(f"{hitalic(self.description)}")
        else:
            preview_list.append("Описание отсутствует ❗️")

        if self.price:
            preview_list.append(f"{hcode(str(self.price) + ' ' + (self.price and self.currency or ''))} "
                                f"{self.price and negotiable or ''}")
        else:
            preview_list.append("Цена не указана ❗️")

        if self.contacts:
            preview_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        else:
            preview_list.append("Контактные данные не указаны ❗️")

        if self.photos_ids:
            preview_list.append(f"Картинки: {len(self.photos_ids)} шт")

        return '\n\n'.join(preview_list)

    def confirm(self) -> str:
        negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'

        confirm_list: list[str] = [
            "Вы уверены что хотите опубликовать пост об объявлении"
            " со следующими данными?",
            f"Теги: {self.make_tags()}",
            f"Описание: {hitalic(self.description)}",
            f"Цена: {hcode(str(self.price) + ' ' + (self.price and self.currency or ''))} "
            f"{self.price and negotiable or ''}",
            f"Контактные данные: {self.humanize_phone_numbers()}",
        ]

        if self.title:
            confirm_list.append(f"Заголовок: {hbold(self.title)}")
        if self.photos_ids:
            confirm_list.append(f"Картинки: {len(self.photos_ids)} шт")

        return '\n\n'.join(confirm_list)

    def post(self) -> str:
        negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'

        post_list: list[str] = [
            self.make_tags()
        ]

        if self.title:
            post_list.append(f"Продается {hbold(self.title)}")

        post_list.append(f"{hitalic(self.description)}")
        post_list.append(f"{hcode(str(self.price) + ' ' + self.currency) + ' ' + negotiable}")
        post_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        post_list.append(f"Телеграм: {self.mention}")
        return '\n\n'.join(post_list)


class PurchaseAd(Ad):
    def to_text(self) -> str:
        description: str = self.description or '➖'
        contacts: str = self.contacts and self.humanize_phone_numbers() or '➖'
        price: float | int | str = self.price or '➖'
        title: str = self.title or '➖'
        photos_len: str = self.photos_ids and str(len(self.photos_ids)) + ' шт' or '➖'

        ttags = self.state == 'tags' and hunderline('Теги') or 'Теги'
        tdescription = self.state == 'description' and hunderline(
            'Описание товара или услуг') or 'Описание товара или услуг'
        tcontact = self.state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'
        tprice = self.state == 'price' and hunderline('Желаемая цена (опционально)') or 'Желаемая цена (опционально)'
        ttitle = self.state == 'title' and hunderline('Заголовок товара или услуг (опционально)') \
                 or 'Заголовок товара или услуг (опционально)'
        tphoto = self.state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'

        return (self.current_heading() +
                f"1. {ttags}: {self.make_tags()}\n"
                f"2. {tdescription}: {hitalic(description)}\n"
                f"3. {tcontact}: {contacts}\n"
                f"4. {tprice}: {hcode(str(price) + ' ' + (self.price and self.currency or ''))}\n"
                f"5. {ttitle}: {hbold(title)}\n"
                f"6. {tphoto}: {photos_len}\n")

    def current_heading(self) -> str:
        match self.state:
            case "tags":
                if not self.tags:
                    return '#️⃣  Выберите тег товара или услуг который вы хотите ' \
                           f'купить нажав по кнопке ниже (макс. <code>{self.tag_limit}</code>):\n\n'
                else:
                    return '#️⃣  Чтобы изменить тег, сначала удалите текущий ' \
                           f'тег, затем установите новый (макс. <code>{self.tag_limit}</code>).\n\n'

            case 'description':
                if not self.description:
                    return '📝 Введите описание товара или услуг которое ' \
                           'вы хотите купить:\n\n'
                else:
                    return '📝 Чтобы изменить описание, просто отправьте ' \
                           'новое описание.\n\n'

            case 'contact':
                if not self.contacts:
                    return '📞 Введите номер телефона который будет отображаться в объявлении ' \
                           f'(макс. <code>{self.contact_limit}</code>):\n\n'
                else:
                    return '📞 Чтобы изменить номер телефона, просто отправьте ' \
                           f'отправьте новый номер (макс. <code>{self.contact_limit}</code>).\n\n'

            case 'price':
                if not self.price:
                    return '💸 Введите желаемую цену товара или услуг и укажите ' \
                           'валюту:\n\n'
                else:
                    return '💸 Чтобы изменить желаемую цену товара или услуг, просто отправьте ' \
                           'новую цену (этот раздел можно пропустить).\n\n'

            case 'title':
                if not self.title:
                    return '🔡 Введите заголовок товара или услуг который вы хотите купить ' \
                           '(этот раздел можно пропустить):\n\n'
                else:
                    return '🔡 Чтобы изменить заголовок товара или услуг, просто отправьте ' \
                           'новое название.\n\n'

            case _:
                if not self.photos_ids:
                    return '🖼 Отправьте картинки товара или услуг который вы хотите купить ' \
                           'по одному (этот раздел можно пропустить).\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>:\n\n'
                else:
                    return '🖼 Чтобы изменить картинку товара или услуг, просто отправьте ' \
                           'новую картинку, а чтобы удалить картинку нажми на ' \
                           'кнопку ниже.\n' \
                           f'P.s. Максимальное количество картинок: <code>{self.pic_limit}</code>'

    def preview(self) -> str:
        preview_list: list[str] = []

        if self.tags:
            preview_list.append(self.make_tags())
        else:
            preview_list.append('Теги не указаны ❗️')

        if self.title:
            preview_list.append(f"Куплю {hbold(self.title)}")

        if self.description:
            preview_list.append(f"{hitalic(self.description)}")
        else:
            preview_list.append("Описание отсутствует ❗️")

        if self.price:
            preview_list.append(f"Желаемая цена: {hcode(str(self.price) + ' ' + self.currency)}")

        if self.contacts:
            preview_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        else:
            preview_list.append("Контактные данные не указаны ❗️")

        if self.photos_ids:
            preview_list.append(f"Картинки: {len(self.photos_ids)} шт")

        return '\n\n'.join(preview_list)

    def confirm(self) -> str:
        confirm_list: list[str] = [
            "Вы уверены что хотите опубликовать пост об объявлении"
            " со следующими данными?",
            f"Теги: {self.make_tags()}",
            f"Описание: {hitalic(self.description)}"
        ]

        if self.price:
            confirm_list.append(f"Желаемая цена: {hcode(str(self.price) + ' ' + self.currency)}")

        confirm_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")

        if self.title:
            confirm_list.append(f"Заголовок: {hbold(self.title)}")
        if self.photos_ids:
            confirm_list.append(f"Картинки: {len(self.photos_ids)} шт")

        return '\n\n'.join(confirm_list)

    def post(self) -> str:
        post_list: list[str] = [
            self.make_tags()
        ]

        if self.title:
            post_list.append(f"Куплю {hbold(self.title)}")

        post_list.append(f"{hitalic(self.description)}")
        if self.price:
            post_list.append(f"{hcode(str(self.price) + ' ' + self.currency)}")
        post_list.append(f"Контактные данные: {self.humanize_phone_numbers()}")
        post_list.append(f"Телеграм: {self.mention}")
        return '\n\n'.join(post_list)
