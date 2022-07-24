import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Counter, ListGroup, ManagedCounterAdapter, Start
from aiogram_dialog.widgets.kbd.list_group import SubManager
from aiogram_dialog.widgets.text import Const, Format

from tgbot.misc.states import ManageRestrictions, AdminPanel
from tgbot.models.restriction import Restriction
from tgbot.services.db_commands import DBCommands


async def get_restriction_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    values: list[int] = await db.get_values_of_restrictions()

    text = (f"Управление ограничениями (эти ограничения устанавливаются "
            f"для всех пользователей):\n\n"
            f"Максимальное количество контактов в объявлении: <code>{values[0]}</code>\n"
            f"Максимальное количество картинок в объявлении: <code>{values[1]}</code>\n"
            f"Максимальное количество постов в день: <code>{values[2]}</code>\n")

    return {"restriction_text": text}


async def get_rest_buttons_data(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    restrictions: list[Restriction] = await db.get_restrictions()

    data = [(item.uid, item.restriction_name, item.number) for item in restrictions]

    return {"rest_buttons": data}


async def change_value(_call: types.CallbackQuery, widget: ManagedCounterAdapter, manager: SubManager):
    session = manager.data.get("session")

    restriction: Restriction = await session.get(Restriction, manager.item_id)
    restriction.number = widget.get_value()
    await session.commit()


async def set_default_restrict_data(_, dialog_manager: DialogManager):
    db: DBCommands = dialog_manager.data.get("db_commands")
    restrictions: list[Restriction] = await db.get_restrictions()

    widget_adtapter = dialog_manager.dialog().find("rest_management")
    contact_widget = widget_adtapter.find_for_item("c", "contact")
    pic_widget = widget_adtapter.find_for_item("c", "pic")
    post_widget = widget_adtapter.find_for_item("c", "post")

    await contact_widget.set_value(value=restrictions[0].number)
    await pic_widget.set_value(value=restrictions[1].number)
    await post_widget.set_value(value=restrictions[2].number)


edit_restrictions_dialog = Dialog(
    Window(
        Format(text="{restriction_text}", when="restriction_text"),
        ListGroup(
            Counter(
                id="c",
                text=Format("({value}) {data[item][1]}"),
                min_value=1,
                on_value_changed=change_value
            ),
            id="rest_management",
            item_id_getter=operator.itemgetter(0),
            items="rest_buttons",
        ),
        Start(
            text=Const("Назад"),
            id="back_to_panel",
            state=AdminPanel.admin
        ),
        state=ManageRestrictions.main,
        getter=[get_restriction_text, get_rest_buttons_data]
    ),
    on_start=set_default_restrict_data
)
