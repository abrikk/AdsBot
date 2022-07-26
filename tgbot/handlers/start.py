from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import CommandStart
from aiogram_dialog import DialogManager, StartMode

from tgbot.config import Config
from tgbot.constants import OWNER, ADMIN, BANNED, USER
from tgbot.misc.states import Main
from tgbot.models.user import User


async def start_bot(message: types.Message, config: Config, session, dialog_manager: DialogManager):
    print("here?")
    user_id = message.from_user.id
    user: User = await session.get(User, user_id)

    if not user:
        role_in_channel = (await message.bot.get_chat_member(config.tg_bot.channel_id, user_id)).status
        if role_in_channel == 'creator':
            role = OWNER
        elif user_id in config.tg_bot.admin_ids or role_in_channel == 'administrator':
            role: str = ADMIN
            role: str = OWNER
        elif role_in_channel == BANNED:
            role: str = BANNED
        else:
            role: str = USER

        user = User(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username,
            last_name=message.from_user.last_name,
            role=role
        )

        session.add(user)
        await session.commit()
        text = (f"Привет, {user.first_name}!\n\n"
                f"Я помогу тебе создать объявление о продаже/покупке "
                f"товаров или услуг. \n\n"
                f"Всё что тебе нужно - это выбрать рубрику ниже"
                f" и следовать дальнейшим инструкциям.\n"
                f"За подробной информацией отправьте команду /help.")
        await dialog_manager.start(state=Main.main, data={
            "start_text": text, "user_role": user.role
        })
    else:
        await dialog_manager.start(state=Main.main, mode=StartMode.RESET_STACK)


def register_start(dp: Dispatcher):
    dp.register_message_handler(start_bot, CommandStart())

