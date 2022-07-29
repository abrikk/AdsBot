import logging

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.utils.exceptions import ChatNotFound, BotBlocked

from tgbot.config import Config


async def set_default_commands(bot: Bot):
    usercommands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="cancel", description="Отменить текущее действие"),
    ]
    await bot.set_my_commands(usercommands, scope=BotCommandScopeDefault())

    admin_commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="cancel", description="Cancel"),
        BotCommand(command="reset_limits", description="Reset limits")
    ]

    my_commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="cancel", description="Cancel"),
        BotCommand(command="show_jobs", description="Show jobs"),
        BotCommand(command="reset_limits", description="Reset limits")
    ]

    try:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=735305633))
        await bot.set_my_commands(my_commands, scope=BotCommandScopeChat(chat_id=569356638))
    except ChatNotFound:
        logging.warning("Forbidden: Chat not found")
    except BotBlocked:
        logging.warning("Forbidden: bot was blocked by the user")
