from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from tgbot.misc.states import Main

start_dialog = Dialog(
    Window(
        Format(text="{start_text}", when="start_text"),
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