import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Start, Button, Row, Back, SwitchTo, Select, Next, Column, Radio, Group, Checkbox, \
    Url
from aiogram_dialog.widgets.text import Format, Const

from tgbot.handlers.create_ad.form import currency_selected, get_currency_data
from tgbot.handlers.edit_ad.edit import edit_input, delete_item, delete_post_ad, save_edit_option, clear_data, \
    save_edit
from tgbot.handlers.edit_ad.getters import get_edit_options, get_edit_text, get_show_my_ad_text, get_post_link, \
    get_can_save_edit
from tgbot.misc.states import ShowMyAd, MyAds


show_my_ad_dialog = Dialog(
    Window(
        Format(text="{preview_text}", when="preview_text"),
        Url(
            text=Const("↪️ Перейти к объявлению"),
            url=Format("{url}"),
        ),
        Next(
            text=Const("🛠 Редактировать"),
        ),
        SwitchTo(
            text=Const("🗑 Удалить"),
            id="delete_post",
            state=ShowMyAd.confirm_delete
        ),
        Start(
            text=Const("🔙 Назад"),
            id="back_to_ma_ads",
            state=MyAds.show,
            mode=StartMode.RESET_STACK,
        ),
        disable_web_page_preview=True,
        state=ShowMyAd.true,
        getter=get_show_my_ad_text
    ),

    Window(
        Const("Выберите раздел который хотите отредактировать:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="edit",
                item_id_getter=operator.itemgetter(0),
                items="edit_options",
                on_click=save_edit_option,
            )
        ),
        Back(text=Const("⬅️ Назад")),
        state=ShowMyAd.show_edit,
        getter=get_edit_options,
        preview_add_transitions=[Next()]
    ),
    Window(
        Format(text="{edit_text}", when="edit_text"),
        Button(
            text=Const("❌ Удалить контакт"),
            id="delete_contact",
            on_click=delete_item,
            when="delete_contact"
        ),
        Button(
            text=Const("❌ Удалить фото"),
            id="delete_photo",
            on_click=delete_item,
            when="delete_photo"
        ),
        Group(
            Checkbox(
                checked_text=Const("Торг уместен: Да ✅"),
                unchecked_text=Const("Торг уместен: Нет ❌"),
                id="negotiable",
                default=False,
                when="show_checkbox"
            ),
            Radio(
                checked_text=Format("✔️ {item[0]}"),
                unchecked_text=Format("{item[0]}"),
                id="currency_code",
                item_id_getter=operator.itemgetter(1),
                items="currencies",
                on_click=currency_selected
            ),
            when="show_currency"
        ),
        Row(
            Back(
                text=Const("⬅️ Отмена"),
                on_click=clear_data
            ),
            Button(
                text=Const("✅ Сохранить"),
                id="save_edit",
                on_click=save_edit,
                when="can_save_edit"
            )
        ),
        MessageInput(
            func=edit_input,
            content_types=[types.ContentType.TEXT, types.ContentType.PHOTO]
        ),
        state=ShowMyAd.edit,
        getter=[get_can_save_edit, get_currency_data, get_edit_text],
        preview_add_transitions=[SwitchTo(Const(""), "hint", ShowMyAd.true)]
    ),
    Window(
        Format("Объвление которое будет удалено: {post_link}\n\n"
               "Вы уверены, что хотите удалить это объявление безвозвратно?"),
        Row(
            SwitchTo(
                Const("❌ Нет"),
                id="delete_post_no",
                state=ShowMyAd.true
            ),
            Button(
                Const("✅ Да"),
                id="yes_delete",
                on_click=delete_post_ad
            )
        ),
        state=ShowMyAd.confirm_delete,
        getter=get_post_link,
        preview_add_transitions=[Start(Const(""), "hint", MyAds.show)]
    )
)
