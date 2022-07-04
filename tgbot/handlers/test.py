from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.types import ChatMemberUpdated

from tgbot.config import load_config, Config
# 1566111340, 304536646

async def test(message: types.Message, config: Config):
    print(config.tg_bot.channel_id)
    member = await message.bot.get_chat_member(str(config.tg_bot.channel_id),
                                               304536646)

    # member = await message.bot.get_chat_administrators(config.tg_bot.channel_id)
    print(member.status)
    await message.answer(str(member))
    # for user in member:
    #     print(user)


def register_test(dp: Dispatcher):
    dp.register_message_handler(test, Command("test"))
