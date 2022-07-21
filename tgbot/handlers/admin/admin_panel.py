from typing import Dict

from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Column, Start
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import AdminPanel, Main, ManageTags, ManageRestrictions


def show_category_buttons(_data: Dict, _widget: Whenable, manager: DialogManager) -> bool:
    return manager.current_context().widget_data.get("tag_categories") is True


def show_tag_buttons(_data: Dict, _widget: Whenable, manager: DialogManager) -> bool:
    return manager.current_context().widget_data.get("tag_names") is True


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
