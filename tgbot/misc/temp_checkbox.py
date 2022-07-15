from typing import Callable, Optional, Union

from aiogram_dialog.context.events import ChatEvent
from aiogram_dialog.manager.protocols import DialogManager
from aiogram_dialog.widgets.kbd.checkbox import BaseCheckbox, OnStateChanged, ManagedCheckboxAdapter
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor


class Checkbox(BaseCheckbox):
    def __init__(self, checked_text: Text, unchecked_text: Text, id: str,
                 on_click: Union[OnStateChanged, WidgetEventProcessor, None] = None,
                 on_state_changed: Optional[OnStateChanged] = None,
                 default: bool = False,
                 when: Union[str, Callable] = None):
        super().__init__(checked_text, unchecked_text, id, on_click, on_state_changed,
                         when)
        self.default = default

    def is_checked(self, manager: DialogManager) -> bool:
        return self.get_widget_data(manager, self.default)

    async def set_checked(self, event: ChatEvent, checked: bool,
                          manager: DialogManager) -> None:
        self.set_widget_data(manager, checked)
        await self.on_state_changed.process_event(
            event, self.managed(manager), manager
        )

    def managed(self, manager: DialogManager):
        return ManagedCheckboxAdapter(self, manager)