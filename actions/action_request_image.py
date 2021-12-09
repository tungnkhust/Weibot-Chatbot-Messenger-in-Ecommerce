import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.utils.utils import get_product_by_object_type
from db_api.product import get_product_by_id
from db_api.product_variant import search_product_variants


class ActionRequestPrice(Action):
    def name(self) -> Text:
        return "action_request_image"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        events = []
        product = None
        object_type = list(tracker.get_latest_entity_values("object_type"))
        colors = list(tracker.get_latest_entity_values("color"))

        if colors:
            events.append(SlotSet("color", colors[0]))
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

        variants = search_product_variants(product_id=product.id, color=colors)

        if len(variants) == 0:
            images = []
            _variants = search_product_variants(product_id=product.id)
            for variant in _variants:
                images.extend(variant.images)
            images = list(set(images))
            if len(images) == 0:
                dispatcher.utter_message(response="utter_fall_back_1")
            else:
                color_text = ", ".join(colors).strip(', ')
                dispatcher.utter_message(response=f"Dạ, hiện tại sản phẩm {product.title} không có màu {color_text}")
                dispatcher.utter_message(response=f"Bạn tham khảo một số màu khác ạ:")
                images = list(set(images))
                for img in images[:3]:
                    dispatcher.utter_message(image=img)
        else:
            images = []

            for variant in variants:
                images.extend(variant.images)

            images = list(set(images))
            dispatcher.utter_message(response="utter_send_image")
            for img in images[:3]:
                dispatcher.utter_message(image=img)

        return events
