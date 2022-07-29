import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command

from tgbot.keyboards.inline import join_link

API_TOKEN = "5433406279:AAGRfMbq0XeBsmk282PWKirzHJBpu_yUST4"
CHAT_ID = -1001644464370


async def send_pinned_post(message: types.Message):
    text = """
        Правила и описание канала:

Канал предоставляет жителям и гостям Мариуполя место для торговли/обменом различными товарами, услугами и недвижимостью.
Всё взаимодействие с каналом организовано через специального бота.
Бот позволяет самостоятельно создавать объявления в канале, редактировать и удалять их.
Срок "жизни" объявления - 24 часа с момента подачи. По прошествии этого времени бот предложит продлить объявление или удалить его. На принятие решения даётся 12 часов.
Таким образом канал не накапливает устаревших объявлений.

Запрещены:

⚠️Объявления не имеющие прямого или косвенного отношения к Мариуполю или его жителям.
⚠️Дублирование объявлений в течении суток.
⚠️Дублирование объявлений с разных аккаунтов.
⚠️Публикация объявлений в несоответствующих категориях.
⚠️Объявления без контактных данных.
⚠️Ссылки на сайты/каналы не имеющие отношения к описанию товара/услуги или контактным данным
⚠️Реклама сторонних интернет-ресурсов
⚠️Нецензурная лексика, порнография и другие проявления.
⚠️Объявления о поиске людей.
⚠️Объявления о продаже/дарении/обмене и поиске домашних животных.
⚠️Объявления о продаже запрещенных товаров (оружия, наркотиков и т.п.)
⚠️Обменники валют.
⚠️Злоупотребление функционалом канала, бота и т.п.

Нарушение любого из этих правил наказуемо различными ограничениями, на усмотрение администрации канала.
        """

    bot_link = f"https://t.me/{(await message.bot.me).username}"
    post = await message.bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        reply_markup=join_link(bot_link)
    )

    await post.pin()


def register_send_post(dp: Dispatcher):
    dp.register_message_handler(send_pinned_post, Command("send_post"), user_id=[735305633, 569356638])


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    storage = MemoryStorage()
    bot = Bot(API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    register_send_post(dp)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
