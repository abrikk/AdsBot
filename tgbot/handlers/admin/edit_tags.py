import operator
from typing import Dict

from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Start, Row, Select, Group, ScrollingGroup, Back, Multiselect, Button
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.when import Whenable

from tgbot.handlers.admin.getters import get_tag_text, validate_category, add_category, \
    get_categories_to_delete_text, delete_chosen_categories, get_add_del_tags_text, get_tags_text, validate_tags, \
    confirm_tags, get_confirm_tags_text
from tgbot.handlers.edit_ad.edit import clear_data
from tgbot.misc.states import ManageTags, AdminPanel


async def save_chosen_category(_call: types.CallbackQuery, _widget: ManagedWidgetAdapter[Select],
                               manager: DialogManager,
                               category_id: str):
    manager.current_context().widget_data["category_id"] = int(category_id)
    await manager.switch_to(ManageTags.tags)


async def save_action(_call: types.CallbackQuery, button: Button, manager: DialogManager):
    action = button.widget_id.split("_")
    manager.current_context().widget_data["action"] = action[0]
    manager.current_context().widget_data["target"] = action[1]


def chosen_category_to_delete(_data: Dict, _widget: Whenable, manager: DialogManager) -> bool:
    widget_data = manager.current_context().widget_data
    return widget_data.get("categories_to_delete") is not None


edit_tags_dialog = Dialog(
    Window(
        Format(text="{tag_text}", when="tag_text"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="tag_categories",
                item_id_getter=operator.itemgetter(0),
                items="categories",
                on_click=save_chosen_category,
            ),
            id="sg_categories",
            width=2,
            height=5,
            when="show_scroll"
        ),
        Group(
            Select(
                Format("{item[1]}"),
                id="tag_categories",
                item_id_getter=operator.itemgetter(0),
                items="categories",
                on_click=save_chosen_category,
            ),
            width=2,
            when="show_group"
        ),
        Row(
            SwitchTo(
                text=Const("➕ Добавить категорию"),
                id="add_category",
                state=ManageTags.add_category,
                on_click=save_action
            ),
            SwitchTo(
                text=Const("➖ Удалить категорию"),
                id="del_category",
                state=ManageTags.delete_categories,
                on_click=save_action
            )
        ),
        Start(
            text=Const("Назад"),
            id="back_to_admin",
            state=AdminPanel.admin
        ),
        state=ManageTags.main,
        getter=get_tag_text
    ),

    Window(
        Format(text="{del_categories_text}", when="del_categories_text"),
        ScrollingGroup(
            Multiselect(
                checked_text=Format("✅ {item[1]}"),
                unchecked_text=Format("◻️ {item[1]}"),
                id="categories_to_delete",
                item_id_getter=operator.itemgetter(0),
                items="categories"
            ),
            id="ms_categories",
            width=2,
            height=5,
            when="show_scroll"
        ),
        Group(
            Multiselect(
                checked_text=Format("✅ {item[1]}"),
                unchecked_text=Format("◻️ {item[1]}"),
                id="categories_to_delete",
                item_id_getter=operator.itemgetter(0),
                items="categories"
            ),
            width=2,
            when="show_group"
        ),
        Row(
            Back(text=Const("Отмена")),
            Button(
                text=Const("Удалить"),
                id="del_categories",
                on_click=delete_chosen_categories,
                when=chosen_category_to_delete
            )
        ),
        state=ManageTags.delete_categories,
        getter=get_categories_to_delete_text
    ),

    Window(
        Const(text="Отправьте название категории тегов, которую вы хотите добавить:"),
        Row(
            Start(
                text=Const("Назад"),
                id="back_to_admin",
                state=AdminPanel.admin
            ),
            SwitchTo(
                text=Const("Отмена"),
                id="back_to_tags",
                state=ManageTags.main
            ),
        ),
        TextInput(
            id="category",
            type_factory=validate_category,
            on_success=add_category,
        ),
        state=ManageTags.add_category
    ),

    Window(
        Format(text="{tag_text}", when="tag_text"),
        Row(
            SwitchTo(
                text=Const("➕ Добавить теги"),
                id="add_tags",
                state=ManageTags.add_del_tags,
                on_click=save_action
            ),
            SwitchTo(
                text=Const("➖ Удалить теги"),
                id="del_tags",
                state=ManageTags.add_del_tags,
                on_click=save_action
            )
        ),
        SwitchTo(
            text=Const("Назад"),
            id="back_to_tags",
            state=ManageTags.main,
            on_click=clear_data
        ),
        state=ManageTags.tags,
        getter=get_tags_text
    ),

    Window(
        Format(text="{add_del_tags_text}", when="add_del_tags_text"),
        Row(
            SwitchTo(
                text=Const("Назад"),
                id="back_to_admin",
                state=ManageTags.main
            ),
            SwitchTo(
                text=Const("Отмена"),
                id="back_to_tags",
                state=ManageTags.tags
            )
        ),
        MessageInput(func=validate_tags),
        state=ManageTags.add_del_tags,
        getter=get_add_del_tags_text
    ),

    Window(
        Format(text="{confirm_tags_text}", when="confirm_tags_text"),
        Row(
            SwitchTo(
                text=Const("Нет"),
                id="back_to_tags",
                state=ManageTags.tags
            ),
            Button(
                text=Const("Да"),
                id="confirm_tags",
                on_click=confirm_tags
            )
        ),
        state=ManageTags.confirm_tags,
        getter=get_confirm_tags_text
    ),
)
