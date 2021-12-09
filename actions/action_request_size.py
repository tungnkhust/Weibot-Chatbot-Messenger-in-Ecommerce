import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.utils.utils import get_product_by_object_type
from db_api.product import get_product_by_id
from db_api.product_variant import search_product_variants


class ActionRequestSize(Action):
    def name(self) -> Text:
        return "action_request_size"

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
            sizes = []
            _variants = search_product_variants(product_id=product.id)
            for variant in _variants:
                sizes.extend(variant.size)
            sizes = list(set(sizes))
            if len(sizes) == 0:
                dispatcher.utter_message(response="utter_fall_back_1")
            else:
                prices_text = ", ".join(sizes).strip(', ')
                text = f"Dạ, Sản phẩm *{product.title}* bên mình đang có các size *{prices_text}* ạ"
                dispatcher.utter_message(text=text)
        else:
            sizes = []

            for variant in variants:
                sizes.append(variant.size)

            sizes = list(set(sizes))

            if len(sizes) == 1:
                sizes_text = str(sizes[0])
            else:
                sizes_text = ", ".join(sizes).strip(', ')

            text = f"Dạ, Sản phẩm *{product.title}* bên mình đang có các size *{sizes_text}* ạ"
            dispatcher.utter_message(text=text)

        return events
