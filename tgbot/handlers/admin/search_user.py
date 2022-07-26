from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter, Text, ContentTypeFilter
from aiogram.utils.markdown import hcode, quote_html, hlink

from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.is_not_sender import IsNotSender
from tgbot.keyboards.inline import join_link
from tgbot.models.user import User


# async def all_queries(query: types.InlineQuery, config: Config):
#     bot = query.bot
#     print("all_queries")
#
#     chat_id = config.tg_bot.channel_id
#     channel_username = (await bot.get_chat(chat_id)).username
#     channel_link = f"https://t.me/{channel_username}"
#     bot_link = f"https://t.me/{(await bot.me).username}"
#
#     bot_involved_text = f"🇺🇦 Присоединяйся! {hlink('Бот', bot_link)} для создания объявлений" \
#                         f" купли-продажи товаров или услуг на канале {channel_link}."
#
#     channel_involved_text = f"🇺🇦 Присоединяйся! {hlink('Канал', channel_link)} с объявлениями о купле/продаже " \
#                             f"товаров или услуг в Мариуполе."
#
#     results = [
#         types.InlineQueryResultArticle(
#             id="share_bot",
#             title="Поделиться ботом 🤖",
#             description="Нажмите на кнопку чтобы поделиться ботом в текущий чат",
#             input_message_content=types.InputTextMessageContent(
#                 message_text=bot_involved_text,
#             ),
#             reply_markup=join_link(bot_link=bot_link, channel_link=channel_link)
#         ),
#         types.InlineQueryResultArticle(
#             id="share_channel",
#             title="Поделиться каналом 🌐",
#             description="Нажмите на кнопку чтобы поделиться каналом объявлений в текущий чат",
#             input_message_content=types.InputTextMessageContent(
#                 message_text=channel_involved_text,
#             ),
#             reply_markup=join_link(bot_link=bot_link, channel_link=channel_link)
#         )
#     ]
#     await query.answer(results=results, cache_time=20)


async def search_user(query: types.InlineQuery, db_commands):
    query_offset = int(query.offset) if query.offset else 0
    users: list[User] = (await db_commands.get_users(
        user_id=query.from_user.id,
        like=query.query.partition(" ")[-1],
        offset=query_offset)
    )

    if users:
        results = [
            types.InlineQueryResultArticle(
                id=str(user.user_id),
                title=quote_html("Пользователь: " + user.first_name + (user.last_name and " " + user.last_name or "")),
                description="Дата регистрации: {date}\n"
                            "Статус: {status}".format(date=user.created_at.strftime('%d.%m.%Y %H:%M:%S'), status=user.role),
                input_message_content=types.InputTextMessageContent(
                    message_text="{name}: {id}".format(
                        name=quote_html(user.first_name),
                        id=hcode(user.user_id)
                    )
                )
            )
            for user in users
        ]
    else:
        results = [
            types.InlineQueryResultCachedGif(
                id="no_such_users",
                gif_file_id="CgACAgIAAxkBAAIoP2LacjY5j_6Kd-ZFVN_CdGqxWUWbAALLGQACFeTZSrIKxiCUKz3FKQQ",
                title="Нет пользователей"
            )
        ]

    if len(users) < 50:
        await query.answer(results=results, cache_time=3, is_personal=True, next_offset="")
    else:
        await query.answer(results, cache_time=3, is_personal=True,
                           next_offset=str(query_offset + 50))


async def manage_user(query: types.InlineQuery, session):
    user_id: int = int(query.query.split(":")[-1].strip())
    user: User = await session.get(User, user_id)

    await query.answer(
        results=[],
        cache_time=3,
        is_personal=True,
        switch_pm_text=quote_html("Пользователь: " + user.first_name + (user.last_name and " " + user.last_name or "")),
        switch_pm_parameter=str(user.user_id),
    )


def register_inline_mode(dp: Dispatcher):
    # dp.register_inline_handler(all_queries, IsNotSender())
    dp.register_inline_handler(search_user, Text(contains="пользователи"), AdminFilter(),
                               ChatTypeFilter(types.ChatType.SENDER))
    dp.register_inline_handler(manage_user, Text(contains="управление пользователем"), AdminFilter(),
                               ChatTypeFilter([types.ChatType.GROUP, types.ChatType.SUPERGROUP]))
