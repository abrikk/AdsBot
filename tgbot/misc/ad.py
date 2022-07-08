from dataclasses import dataclass, field

import flag
import phonenumbers
from aiogram.utils.markdown import hunderline, hbold, hitalic


@dataclass
class Ad:
    state: str
    tags: list[str] = field(default_factory=list)
    title: str = field(default_factory=str)
    description: str = field(default_factory=str)
    price: float | int = field(default_factory=float)
    contacts: list[str] = field(default_factory=list)
    photos_ids: list[str] = field(default_factory=list)

    def to_text(self):
        raise NotImplementedError("Can't instantiate an abstract method.")

    def current_heading(self) -> str:
        raise NotImplementedError("Can't instantiate an abstract method.")

    @staticmethod
    def humanize_phone_numbers(phone_numbers: list[str]) -> str:
        list_of_numbers: list[str] = list()
        for number in phone_numbers:
            if not number.startswith('+'):
                number = '+' + number
            number = phonenumbers.parse(number)
            emoji = ' ' + flag.flag(f"{phonenumbers.region_code_for_country_code(number.country_code)}")
            list_of_numbers.append(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL) + emoji)

        return ", ".join(list_of_numbers)


class SalesAd(Ad):
    currency: str = "₴"
    negotiable: bool = False

    def to_text(self) -> str:
        title: str = self.title or '➖'
        description: str = self.description or '➖'
        price: float | int | str = self.price or '➖'
        negotiable: str = '(торг уместен)' if self.negotiable else '(цена окончательна)'
        contacts: str = self.contacts and self.humanize_phone_number(self.contacts) or '➖'

        photos_len: str = self.photos_ids and str(len(self.photos_ids)) + ' шт' or '➖'

        ttitle = self.state == 'title' and hunderline('Заголовок товара или услуг') or 'Заголовок товара или услуг'
        tdescription = self.state == 'description' and hunderline('Описание товара или услуг') or 'Описание товара или услуг'
        tprice = self.state == 'price' and hunderline('Цена') or 'Цена'
        tcontact = self.state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'
        tphoto = self.state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'
        ttags = self.state == 'tags' and hunderline('Теги') or 'Теги'

        (f"1. {ttitle}: {hbold(title)}\n"
         f"2. {tdescription}: {hitalic(description)}\n"
         f"3. {tprice}: {hcode(str(price) + ' ' + (data.get('price') and currency or ''))} {data.get('price') and negotiable or ''}\n"
         f"4. {tcontact}: {hcode(contact)}\n"
         f"5. {tphoto}: {photo}\n"
         f"6. {ttags}: {tags}\n")


    def current_heading(self) -> str:
        match self.state:
            case 'title':
                if not self.title:
                    return '🔡 Введите заголовок товара или услуг (этот раздел можно пропустить):\n\n'
                else:
                    return '🔡 Чтобы изменить заголовок товара или услуг, просто отправьте' \
                           'новое название.\n\n'

            case 'description':
                if not self.description:
                    return '📝 Введите описание товара или услуг. :\n\n'
                else:
                    return '📝 Чтобы изменить описание товара или услуг, просто отправьте' \
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
                    return '📞 Введите номер телефона который будет отображаться в объявлении:\n\n'
                else:
                    return '📞 Чтобы изменить номер телефона, просто отправьте' \
                           'отправьте новый номер.\n\n'

            case 'photo':
                if not self.photos_ids:
                    return '🖼 Отправьте картинки товара или услуг по одному ' \
                           '(этот раздел можно пропустить).\n' \
                           'P.s. Максимальное количество картинок: <code>5</code>:\n\n'
                else:
                    return '🖼 Чтобы изменить картинку товара или услуг, просто отправьте' \
                           'новую картинку, а чтобы удалить картинку нажми на ' \
                           'кнопку ниже.\n\n'

            case _:
                if not self.tags:
                    return '#️⃣  Выберите тег своего товара или услуг нажав по кнопке ' \
                           'ниже:\n\n'
                else:
                    return '#️⃣  Чтобы изменить тег товара или услуг, сначала удалите текущий ' \
                           'тег, затем установите новый.\n\n'


class PurchaseAd(Ad):
    def to_text(self) -> str:
        pass

    def current_heading(self) -> str:
        pass

