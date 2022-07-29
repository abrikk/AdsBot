import logging

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import MessageToDeleteNotFound, BotBlocked
from aiogram.utils.markdown import hstrikethrough
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.handlers.create_ad.form import get_user_mention, make_link_to_post
from tgbot.keyboards.inline import confirm_delete_ad, manage_cb, manage_post, confirm_cb
from tgbot.models.post_ad import PostAd
from tgbot.services.db_commands import DBCommands


async def manage_post_ad(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    post_id: str = callback_data.get("post_id")
    user_id: str = callback_data.get("user_id")
    full_name: str = callback_data.get("full_name")

    await call.message.edit_text(
        text=call.message.text + "\n\n ⚠️ Вы уверены что хотите удалить это объявление?",
        reply_markup=confirm_delete_ad(post_id, user_id, full_name)
    )


async def delete_ad_confirmation(call: types.CallbackQuery, callback_data: dict, session,
                                 db_commands: DBCommands, config: Config):
    await call.answer()
    post_id: int = int(callback_data.get("post_id"))
    action: str = callback_data.get("action")
    channel = await call.bot.get_chat(config.chats.main_channel_id)
    post_link: str = make_link_to_post(channel_username=channel.username, post_id=post_id)

    if action == "no":
        await call.message.edit_text(
            text=call.message.text.replace("\n\n ⚠️ Вы уверены что хотите удалить это объявление?", ""),
            reply_markup=manage_post(post_id=post_id, user_id=call.from_user.id,
                                     full_name=call.from_user.full_name, url=post_link)
        )
    else:
        scheduler: AsyncIOScheduler = call.bot.get("scheduler")
        user_id: int = int(callback_data.get("user_id"))
        full_name: str = callback_data.get("full_name")

        post_ad: PostAd = await session.get(PostAd, int(post_id))
        try:
            if post_ad.related_messages:
                for message in post_ad.related_messages:
                    await call.bot.delete_message(
                        chat_id=config.chats.main_channel_id,
                        message_id=message.message_id
                    )
            else:
                await call.bot.delete_message(
                    chat_id=config.chats.main_channel_id,
                    message_id=post_ad.post_id
                )
        except MessageToDeleteNotFound:
            logging.warning("Message to delete not found by administrator")

        try:
            scheduler.remove_job("ask_" + str(post_ad.post_id))
            scheduler.remove_job("check_" + str(post_ad.post_id))
        except JobLookupError:
            logging.warning("Job not found")

        support_ids: list[int, str, str | None, str | None] = await db_commands.get_support_team()
        support_mentions: str = ", ".join([
            get_user_mention(id, first_name, last_name, username)
            for id, first_name, last_name, username in support_ids
        ])

        post_delete_text = (f"«{post_ad.description}»\n\n"
                            f"❗️ Ваше объявление с данным описанием было удалено администрацией канала, "
                            f"в связи с тем, что оно не соответстовало правилам публикации объявление.\n\n"
                            f"Если вы считаете, что это ошибка, пожалуйста, обратитесь к службе поддержки канала:"
                            f" {support_mentions}")

        await session.delete(post_ad)
        await session.commit()
        try:
            await call.bot.send_message(
                chat_id=user_id,
                text=post_delete_text,
                disable_web_page_preview=True
            )
        except BotBlocked as exc:
            logging.warning(exc)

        await call.message.edit_text(
            text="#УдаленоАдминистратором\n\n" +
            hstrikethrough(call.message.text.replace("\n\n ⚠️ Вы уверены что хотите удалить это объявление?", "")) +
            f"\n\n Объявление было удалено администратором: {call.from_user.get_mention()}‼️",
            reply_markup=manage_post(user_id, full_name, argument="only_search_user")
        )

        await call.answer(text="Объявление было успешно удалено!", show_alert=True)


def register_manage_post_ad(dp: Dispatcher):
    dp.register_callback_query_handler(manage_post_ad, manage_cb.filter())
    dp.register_callback_query_handler(delete_ad_confirmation, confirm_cb.filter())
