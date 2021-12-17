from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants
from db_api.schema import Product
from actions.utils.utils import get_product_by_object_type


class ActionInformProductInfo(Action):
    def name(self) -> Text:
        return "action_inform_product_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = list()
        pre_intent = tracker.get_slot("intent")

        if pre_intent is None:
            dispatcher.utter_message(text="Bạn muốn hỏi thông tin sản phẩm nào ạ")
            event.append(FollowupAction("action_suggest_product_by_entity"))
            return event

        if pre_intent in [
            "request_product",
            "request_info",
            "request_image",
            "request_color",
            "request_size",
            "request_price",
            "request_order"
        ]:
            event.append(FollowupAction(f"action_{pre_intent}"))
            return event

        return event
