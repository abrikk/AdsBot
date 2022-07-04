from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from tgbot.config import Config
from tgbot.misc.states import Main
from tgbot.models.user import User


async def get_main_text(dialog_manager: DialogManager, **_kwargs):
    session = dialog_manager.data.get("session")
    config: Config = dialog_manager.data.get("config")
    obj = dialog_manager.event

    user_id = obj.from_user.id
    user: User = await session.get(User, user_id)

    if not user:
        role_in_channel = (await obj.bot.get_chat_member(config.tg_bot.channel_id, user_id)).status
        if user_id in config.tg_bot.admin_ids or role_in_channel in ["creator", "administrator"]:
            role: str = "admin"
        else:
            role: str = "user"

        user = User(
            user_id=user_id,
            first_name=obj.from_user.first_name,
            username=obj.from_user.username,
            last_name=obj.from_user.last_name,
            role=role
        )

        session.add(user)
        await session.commit()


main_dialog = Dialog(
    Window(
        Format(text="{main_text}", when="main_text"),
        Row(
            SwitchTo(
                text=Const("Продам"),
                id="sell",
                state=Main.sell
            ),
            SwitchTo(
                text=Const("Куплю"),
                id="buy",
                state=Main.buy
            ),
        ),
        state=Main.main,
        getter=get_main_text
    )
)