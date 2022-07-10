from typing import List, Callable, Optional, Union, Dict

from aiogram.types import InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.text import Text


class SwitchInlineQueryCurrentChat(Keyboard):
    def __init__(self, text: Text, switch_inline_query_current_chat: Text = Text(""),
                 id: Optional[str] = None, when: Union[str, Callable, None] = None):
        super().__init__(id, when)
        self.text = text
        self.switch_inline_query_current_chat = switch_inline_query_current_chat

    async def _render_keyboard(self, data: Dict, manager: DialogManager) -> List[List[InlineKeyboardButton]]:
        return [[
            InlineKeyboardButton(
                text=await self.text.render_text(data, manager),
                switch_inline_query_current_chat=await self.switch_inline_query_current_chat.render_text(data, manager)
            )
        ]]
