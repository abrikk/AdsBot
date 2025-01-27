from aiogram import Dispatcher, types
from aiogram.utils.exceptions import MessageCantBeDeleted

from tgbot.filters.is_group import IsGroup
from tgbot.services.db_commands import DBCommands


async def proccess_chat_join_user(member: types.ChatMemberUpdated, db_commands: DBCommands):
    support_ids: list[int] = await db_commands.get_support_team_ids()
    bot = await member.bot.me

    if member.new_chat_member.is_chat_member() and member.from_user.id not in support_ids \
            or member.from_user.id not in (569356638, bot.id):
        await member.bot.unban_chat_member(
            chat_id=member.chat.id,
            user_id=member.from_user.id
        )


async def clean_chat_member_updated(message: types.Message):
    try:
        await message.delete()
    except MessageCantBeDeleted:
        pass


def register_group_approval(dp: Dispatcher):
    dp.register_message_handler(clean_chat_member_updated, IsGroup(), content_types=[
        types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER
    ])
    dp.register_chat_member_handler(proccess_chat_join_user, IsGroup())
