import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.product import get_product_by_id, search_products
from actions.utils.product_utils import get_url
import random


class ActionRequestProduct(Action):
    def name(self) -> Text:
        return "action_request_product"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event = []

        object_types = tracker.get_latest_entity_values(entity_type="object_type")
        object_types = list(object_types)

        gender = list(tracker.get_latest_entity_values(entity_type="gender"))
        if len(set(gender)) != 1:
            gender = None
        else:
            gender = gender[0]
        colors = list(tracker.get_latest_entity_values(entity_type="color"))
        event.append(SlotSet(key="gender", value=gender))
        products = []

        if colors:
            color = colors[0]
            for object_value in object_types:
                _products = search_products(product_type=object_value, color=color, gender=gender)
                products.extend(_products)
                event.append(SlotSet(key="color", value=color))
        else:
            for object_value in object_types:
                _products = search_products(product_type=object_value, gender=gender)
                products.extend(_products)

        if len(products) == 0:
            event.append(SlotSet("request_no_has", True))
            event.append(SlotSet("object_type", []))
            if object_types:
                dispatcher.utter_message(text=f"Sản phẩm {object_types[0]} hiện bên mình không có ạ")
            else:
                if (colors is None) and (gender is None):
                    dispatcher.utter_message(text=f"Sản phẩm bạn tìm kiếm hiện bên mình không có ạ")

            event.append(FollowupAction("action_suggest_product_by_entity"))
            return event

        if len(products) > 10:
            random.shuffle(products)
            products = products[:10]

        elements = []
        product_ids = []
        for product in products:
            element = product.to_messenger_element()
            elements.append(element)
            product_ids.append(product.id)

        message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        }

        dispatcher.utter_message(text="Bên mình hiên đang có những sản phẩm sau bạn tham khảo ạ:")
        dispatcher.utter_message(json_message=message)
        event.append(SlotSet(key="product_ids", value=product_ids))

        event.append(SlotSet(key="object_type", value=object_types))
        if len(product_ids) == 1:
            event.append(SlotSet(key="product_id", value=product_ids[0]))
        else:
            event.append(SlotSet(key="product_id", value=None))
        event.append(SlotSet("request_no_has", None))

        return event
