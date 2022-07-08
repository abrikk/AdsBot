from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Row, Start
from aiogram_dialog.widgets.text import Format, Const

from tgbot.misc.states import Main, Buy, Sell


async def get_main_text(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.current_context().start_data

    if start_data and (text := start_data.get("start_text")):
        start_data.clear()
        return {"main_text": text}

    return {"main_text": "Что будем делать?"}


main_dialog = Dialog(
    Window(
        Format(text="{main_text}", when="main_text"),
        Row(
            Start(
                text=Const("Куплю"),
                id="buy",
                state=Buy.tags
            ),
            Start(
                text=Const("Продам"),
                id="sell",
                state=Sell.tags
            )
        ),
        state=Main.main,
        getter=get_main_text
    )
)
