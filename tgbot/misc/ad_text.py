from dataclasses import dataclass

from tgbot.misc.ad import Ad


@dataclass
class AdText:
    ad: Ad

    def tags_buy(self) -> str:
        return '#️⃣  Выберите тег товара или услуг который вы хотите ' \
               f'купить нажав по кнопке ниже (макс. <code>{self.ad.tag_limit}</code>):\n\n'