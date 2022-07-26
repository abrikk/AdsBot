from aiogram import types
from aiogram.utils.markdown import hcode, hbold
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import T
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.exc import IntegrityError

from tgbot.misc.states import ManageTags
from tgbot.models.tag_category import TagCategory
from tgbot.models.tags_name import TagName
from tgbot.models.user import User
from tgbot.services.db_commands import DBCommands


async def get_main_tags_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    tags: list[tuple[str, str]] = await db.get_tags()
    tag_categories: dict[str, list[str]] = {}
    categories: list = await db.get_categories()

    for category, name in tags:
        if category not in tag_categories:
            tag_categories[category] = []
        tag_categories[category].append(name)

    tags_text = "\n\n".join(
        [f"<b>{category}</b>: " + ", ".join(map(hcode, tags_list)) for category, tags_list in tag_categories.items()])
    tags_count = sum([len(tags_list) for tags_list in tag_categories.values()])

    inactive_count: int = len(categories) - len(tag_categories)

    emoji: str = (inactive_count > 0) and "⚠" or "✅️"

    text = (f"⚙️ Управление тегами:\n\n"
            f"Чтобы добавить или удалить теги в категории, выберите ту категорию в "
            f"которую хотите добавить или удалить тег.\n\n"
            f"✅ Всего активных категорий тегов: <code>{len(tag_categories)}</code>\n"
            f"{emoji} Всего неактивных категорий тегов: <code>{inactive_count}</code>\n"
            f"#️⃣ Всего тегов: <code>{tags_count}</code>\n\n"
            f"{tags_text}")

    return {
        "tag_text": text,
        "categories": [(str(id), category) for id, category in categories],
        "show_scroll": len(categories) > 10,
        "show_group": len(categories) <= 10,
    }


async def get_categories_to_delete_text(dialog_manager: DialogManager, **_kwargs):
    db: DBCommands = dialog_manager.data.get("db_commands")
    categories: list = await db.get_categories()

    text = "Выберите категории тегов, которые вы хотите удалить:"
    return {
        "del_categories_text": text,
        "categories": [(str(id), category) for id, category in categories],
        "show_scroll": len(categories) > 10,
        "show_group": len(categories) <= 10,
    }


async def get_tags_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    session = dialog_manager.data.get("session")
    db: DBCommands = dialog_manager.data.get("db_commands")
    category_id: int = widget_data.get("category_id")
    category: str = widget_data.get("category")
    if not category:
        category: TagCategory = await session.get(TagCategory, category_id)
        category = widget_data["category"] = category.category
    tag_names: list[TagName] = await db.get_tags_of_category(category)

    text = (f"Категория тегов: <code>{category}</code>\n\n"
            f"Всего тегов в этой категории: <code>{len(tag_names)}</code>\n\n")

    if tag_names:
        text += f"Текущие теги в данной категории: {', '.join([hcode(name) for id, name in tag_names])}"
    else:
        text += f"⚠️ Эта категория не активна. Чтобы активировать ее добавьте в нее хотя бы один тег."

    return {"tag_text": text, "show_delete_tags": len(tag_names) > 0}


async def get_add_del_tags_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    action: str = widget_data.get("action")
    action_text: str = "добавить" if action == "add" else "удалить"

    db: DBCommands = dialog_manager.data.get("db_commands")
    category: str = widget_data.get("category")
    tag_names: list[TagName] = await db.get_tags_of_category(category)

    text = (f"Отправьте тег который хотите {action_text}."
            f"Чтобы {action_text} несколько тегов введите их через пробел.\n\n"
            f"Категория тегов: <code>{category}</code>\n\n"
            f"Всего тегов в этой категории: <code>{len(tag_names)}</code>\n\n"
            f"Текущие теги в данной категории: {', '.join([hcode(name) for id, name in tag_names])}")
    return {"add_del_tags_text": text}


async def get_confirm_tags_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    action: str = widget_data.get("action")
    action_text: str = "добавить" if action == "add" else "удалить"
    tags: list = widget_data.get("tags")
    category = widget_data.get("category")

    category_text = "в категорию" if action == "add" else "из категории"

    text = (f"Вы уверены, что хотите {action_text} следующие теги {category_text} <b>{category}</b>?\n\n"
            f"Теги: {', '.join(map(hcode, tags))}")

    return {"confirm_tags_text": text}


async def get_confirm_categories_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    session = dialog_manager.data.get("session")
    categories_id = map(int, widget_data.get("categories_to_delete"))
    categories: list[TagCategory] = [await session.get(TagCategory, id) for id in categories_id]

    text = (f"Вы уверены, что хотите удалить следующие категории тегов?"
            f"Категории которые будут удалены: {', '.join(map(hbold, [category.category for category in categories]))}")

    return {"confirm_categories_text": text}


async def add_category(message: types.Message, _widget: TextInput, manager: DialogManager,
                       category: T):
    session = manager.data.get("session")
    try:
        category: TagCategory = TagCategory(category=category)
        session.add(category)
        await session.commit()
        await message.answer("Категория тегов добавлена.")
        manager.current_context().widget_data.clear()
        await manager.switch_to(ManageTags.main)
    except IntegrityError:
        await session.rollback()
        manager.show_mode = ShowMode.EDIT
        await message.answer("Категория тегов с таким названием уже существует.")


async def confirm_tags(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data

    session = manager.data.get("session")
    action: str = widget_data.get("action")
    tags: list = widget_data.get("tags")
    category = widget_data.get("category")

    if action == "add":
        try:
            tags_obj: list[TagName] = [
                TagName(
                    category=category,
                    name=tag
                ) for tag in tags
            ]
            session.add_all(
                (
                    *tags_obj,
                 )
            )
        except IntegrityError:
            await session.rollback()

    else:
        tags_id: list[int] = widget_data.get("tags_id")
        for tag_id in tags_id:
            tag_obj = await session.get(TagName, tag_id)
            await session.delete(tag_obj)
        widget_data.pop("tags_id")
    await session.commit()
    success_text = "добавлены" if action == "add" else "удалены"
    await call.answer(f"Теги успешно было {success_text}!")

    items_to_pop = ["tags", "target", "action", "category"]
    for item in items_to_pop:
        widget_data.pop(item)
    await manager.switch_to(ManageTags.tags)


async def delete_chosen_categories(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    session = manager.data.get("session")
    categories_id = map(int, widget_data.get("categories_to_delete"))
    categories: list[TagCategory] = [await session.get(TagCategory, id) for id in categories_id]
    for category in categories:
        await session.delete(category)
    await session.commit()
    widget_data.clear()
    await call.message.answer("Категории тегов были успешно удалены.")
    await manager.switch_to(ManageTags.main)


async def validate_tags(message: types.Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    tags: list = list(set(map(lambda t: t.replace(",", "").capitalize(), message.text.split())))
    print(tags)
    action: str = widget_data.get("action")
    if action == "del":
        category: str = widget_data.get("category")
        db: DBCommands = manager.data.get("db_commands")
        for tag in tags:
            tag_id = await db.get_tags_by_category_and_name(category, tag)
            print("id tag by categoru and  name:", tag_id)
            if not tag_id:
                print("no tag", tags)
                tags.remove(tag)
                continue
            print("what it gives", widget_data.setdefault("tags_id", []))
            tags_id: list[int] = widget_data.setdefault("tags_id", [])
            tags_id.append(tag_id)
        if not tags:
            return
    print("FINALLY", tags)
    widget_data["tags"] = tags
    await dialog.switch_to(ManageTags.confirm_tags)


def validate_category(category: str):
    return "_".join(category.split()).capitalize()
    # return category.strip().capitalize()
