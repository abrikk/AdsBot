from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Column, Start
from aiogram_dialog.widgets.text import Format, Const

from tgbot.misc.states import AdminPanel, Main, ManageTags, ManageRestrictions

admin_dialog = Dialog(
    Window(
        Format(text="Выберите раздел в который хотите перейти: "),
        Column(
            Start(
                text=Const("⚙️ Ограничения"),
                id="restrictions",
                state=ManageRestrictions.main,
                mode=StartMode.RESET_STACK
            ),
            Start(
                text=Const("#️⃣ Теги"),
                id="tags",
                state=ManageTags.main,
                mode=StartMode.RESET_STACK
            ),
            Start(
                text=Const("🔙 Назад"),
                id="back_to_main",
                state=Main.main,
                mode=StartMode.RESET_STACK
            )
        ),
        state=AdminPanel.admin
    )
)
