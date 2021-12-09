import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.utils.utils import get_product_by_object_type
from db_api.product import get_product_by_id
from db_api.product_variant import search_product_variants


class ActionRequestImage(Action):
    def name(self) -> Text:
        return "action_request_price"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        events = []
        product = None
        object_type = list(tracker.get_latest_entity_values("object_type"))

        if len(object_type) == 0:
            product_id = tracker.get_slot("product_id")
            if product_id is None:
                dispatcher.utter_message(text="Bạn muốn xem sản phẩm nào ạ?")
                return events
            else:
                product = get_product_by_id(product_id)
        else:
            products = [get_product_by_id(p_id) for p_id in tracker.get_slot("product_ids")]
            product = get_product_by_object_type(object_type[0], products)

            events.append(SlotSet("object_type", object_type))
            events.append(SlotSet("product_id", product.id))

        variants = search_product_variants(product_id=product.id)

        if len(variants) == 0:
            prices = []
            _variants = search_product_variants(product_id=product.id)
            for variant in _variants:
                prices.extend(variant.price)
            prices = list(set(prices))
            if len(prices) == 0:
                dispatcher.utter_message(response="utter_fall_back_1")
            else:
                prices_text = ", ".join(prices).strip(', ')
                text = f"Dạ, Sản phẩm *{product.title}* bên mình đang có giá như sau: {prices_text} ạ"
                dispatcher.utter_message(text=text)
        else:
            prices = []

            for variant in variants:
                prices.append(variant.price)

            prices = list(set(prices))

            if len(prices) == 1:
                prices_text = str(prices[0])
            else:
                prices_text = ", ".join(prices).strip(', ')

            text = f"Dạ, Sản phẩm *{product.title}* bên mình đang có giá *{prices_text}* ạ"
            dispatcher.utter_message(text=text)

        return events
