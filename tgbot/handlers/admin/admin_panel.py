import operator

from aiogram import types
from aiogram.utils.markdown import hcode
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Column, SwitchTo, Group, Back, ListGroup, Counter, ManagedCounterAdapter, Start
from aiogram_dialog.widgets.kbd.list_group import SubManager
from aiogram_dialog.widgets.text import Format, Const

from tgbot.misc.states import AdminPanel, Main
from tgbot.models.restriction import Restriction
from tgbot.models.tag import Tag
from tgbot.services.db_commands import DBCommands


async def get_restriction_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    values: list[int] = await db.get_values_of_restrictions()

    text = (f"Управление ограничениями (эти ограничения устанавливаются "
            f"для всех пользователей):\n\n"
            f"Максимальное количество тегов в объявлении: <code>{values[0]}</code>\n"
            f"Максимальное количество контактов в объявлении: <code>{values[1]}</code>\n"
            f"Максимальное количество картинок в объявлении: <code>{values[2]}</code>\n"
            f"Максимальное количество постов в день: <code>{values[3]}</code>\n")

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
    tag_widget = widget_adtapter.find_for_item("c", "tag")
    contact_widget = widget_adtapter.find_for_item("c", "contact")
    pic_widget = widget_adtapter.find_for_item("c", "pic")
    post_widget = widget_adtapter.find_for_item("c", "post")

    await tag_widget.set_value(value=restrictions[0].number)
    await contact_widget.set_value(value=restrictions[1].number)
    await pic_widget.set_value(value=restrictions[2].number)
    await post_widget.set_value(value=restrictions[3].number)


async def get_tag_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    tags: list[str] = await db.get_tags()

    text = (f"Управление тегами:\n\n"
            f"Всего тегов: <code>{len(tags)}</code>\n"
            f"Теги: {', '.join(map(hcode, ['#' + tag for tag in tags]))}\n")

    return {"tag_text": text}


async def get_add_del_text(dialog_manager: DialogManager, **_kwargs):
    state: str = dialog_manager.current_context().state.state.split(":")[-1]
    db: DBCommands = dialog_manager.data.get("db_commands")
    tags: list[str] = await db.get_tags()

    action: str = "добавить" if state == "add_tag" else "удалить"

    text = (f"Отправьте тег который хотите {action}."
            f"Чтобы {action} несколько тегов введите их через пробел.\n\n"
            f"Всего тегов: <code>{len(tags)}</code>\n"
            f"Теги: {', '.join(map(hcode, ['#' + tag for tag in tags]))}\n")

    return {"add_del_text": text}


def validate_tags(tags: str):
    return list(map(lambda tag: tag.removeprefix("#"), tags.lower().split()))


async def add_del_tags(_message: types.Message, _widget: TextInput, manager: DialogManager, tags: list[str]):
    state: str = manager.current_context().state.state.split(":")[-1]
    session = manager.data.get("session")

    match state:
        case "add_tag":
            tags_obj: list[Tag] = [
                Tag(tag_name=tag_name) for tag_name in tags
                if not await session.get(Tag, tag_name)
            ]
            session.add_all(
                (
                    *tags_obj,
                )
            )
        case _:
            tags_obj: list[Tag] = [
                await session.get(Tag, tag_name) for tag_name in tags
                if tag_name not in ("продам", "куплю") and session.get(Tag, tag_name)
            ]
            for tag in tags_obj:
                await session.delete(tag)
    await session.commit()

    await manager.switch_to(AdminPanel.tag)


admin_dialog = Dialog(
    Window(
        Format(text="Выберите раздел в который хотите перейти: "),
        Column(
            Group(
                SwitchTo(
                    text=Const("⚙️ Ограничения"),
                    id="restrictions",
                    state=AdminPanel.restriction
                ),
                SwitchTo(
                    text=Const("#️⃣ Теги"),
                    id="tags",
                    state=AdminPanel.tag,
                )),
            Start(
                text=Const("🔙 Назад"),
                id="back_to_main",
                state=Main.main,
                mode=StartMode.RESET_STACK
            )),
        state=AdminPanel.admin
    ),
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
        Back(
            text=Const("Назад")
        ),
        state=AdminPanel.restriction,
        getter=[get_restriction_text, get_rest_buttons_data]
    ),
    Window(
        Format(text="{tag_text}", when="tag_text"),
        SwitchTo(
            text=Const("➕ Добавить тег"),
            id="add_tag",
            state=AdminPanel.add_tag
        ),
        SwitchTo(
            text=Const("➖ Удалить тег"),
            id="del_tag",
            state=AdminPanel.del_tag
        ),
        SwitchTo(
            text=Const("Назад"),
            id="back_to_admin",
            state=AdminPanel.admin
        ),
        state=AdminPanel.tag,
        getter=get_tag_text
    ),
    Window(
        Format(text="{add_del_text}", when="add_del_text"),
        SwitchTo(
            text=Const("Отмена"),
            id="back_to_tags",
            state=AdminPanel.tag
        ),
        SwitchTo(
            text=Const("Назад"),
            id="back_to_admin",
            state=AdminPanel.admin
        ),
        TextInput(
            id="tags_input",
            type_factory=validate_tags,
            on_success=add_del_tags,
        ),
        state=AdminPanel.add_tag,
        getter=get_add_del_text
    ),
    Window(
        Format(text="{add_del_text}", when="add_del_text"),
        SwitchTo(
            text=Const("Отмена"),
            id="back_to_tags",
            state=AdminPanel.tag
        ),
        SwitchTo(
            text=Const("Назад"),
            id="back_to_admin",
            state=AdminPanel.admin
        ),
        TextInput(
            id="tags_input",
            type_factory=validate_tags,
            on_success=add_del_tags,
        ),
        state=AdminPanel.del_tag,
        getter=get_add_del_text
    ),
    on_start=set_default_restrict_data
)
