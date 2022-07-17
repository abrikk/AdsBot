from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter, Text
from aiogram.utils.markdown import hcode, quote_html

from tgbot.filters.admin import AdminFilter
from tgbot.models.user import User


async def all_queries(query: types.InlineQuery):
    bot = query.bot.me
    involved_text = "Присоединяйся! "
    results = [
        types.InlineQueryResultArticle(
            id=str(user.user_id),
            title="Поделиться ботом 🌐",
            description="Нажмите на кнопку чтобы поделиться ботом в текущий чат",
            input_message_content=types.InputTextMessageContent(
                message_text="{name}: {id}".format(
                    name=quote_html(user.first_name),
                    id=hcode(user.user_id)
                )
            )
        )
        for user in users
    ]
    await query.answer(results=results, cache_time=3, is_personal=True, next_offset="")


async def search_user(query: types.InlineQuery, db_commands):
    query_offset = int(query.offset) if query.offset else 0
    users: list[User] = (await db_commands.get_users(
        user_id=query.from_user.id,
        like=query.query.partition(" ")[-1],
        offset=query_offset)
    )

    results = [
        types.InlineQueryResultArticle(
            id=str(user.user_id),
            title=quote_html("Пользователь: " + user.first_name + (user.last_name and " " + user.last_name or "")),
            description="Дата регистрации: {date}".format(date=user.created_at.strftime('%d.%m.%Y %H:%M:%S')),
            input_message_content=types.InputTextMessageContent(
                message_text="{name}: {id}".format(
                    name=quote_html(user.first_name),
                    id=hcode(user.user_id)
                )
            )
        )
        for user in users
    ]
    if len(users) < 50:
        await query.answer(results=results, cache_time=3, is_personal=True, next_offset="")
    else:
        await query.answer(results, cache_time=3, is_personal=True,
                           next_offset=str(query_offset + 50))


def register_inline_mode(dp: Dispatcher):
    dp.register_inline_handler(search_user, Text(contains="пользователи"), AdminFilter(),
                               ChatTypeFilter(types.ChatType.SENDER))
