import copy

from aiogram_dialog import DialogManager

from tgbot.handlers.buy_and_sell.sell import get_active_section
from tgbot.misc.ad import PurchaseAd


async def get_buy_text(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.current_context().widget_data
    print(data)
    sell_data = copy.deepcopy(data)
    sell_data.pop('currency_code', None)

    state = dialog_manager.current_context().state.state.split(":")[-1]

    sell_ad = PurchaseAd(state=state, **sell_data)

    return {"buy_text": sell_ad.to_text(), "page": get_active_section(state)}

