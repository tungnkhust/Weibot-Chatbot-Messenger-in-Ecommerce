import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
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

        events = []

        object_types = tracker.get_latest_entity_values(entity_type="object_type")
        object_types = list(object_types)

        gender = list(tracker.get_latest_entity_values(entity_type="gender"))
        if len(set(gender)) != 1:
            gender = None

        colors = list(tracker.get_latest_entity_values(entity_type="color"))
        # prices = list(tracker.get_latest_entity_values(entity_type="size"))

        events.append(SlotSet(key="object_type", value=object_types))
        events.append(SlotSet(key="gender", value=gender))
        products = []

        if colors:
            color = colors[0]
            for object_value in object_types:
                _products = search_products(product_type=object_value, color=color, gender=gender)
                products.extend(_products)
                events.append(SlotSet(key="color", value=color))
        else:
            for object_value in object_types:
                _products = search_products(product_type=object_value, gender=gender)
                products.extend(_products)

        if len(products) > 10:
            random.shuffle(products)
            products = products[:10]

        if len(products) == 0:
            dispatcher.utter_message(text="Dạ, hiện tại mình không tìm thấy sản phẩm trong kho."
                                          " Bạn lên đây để tìm thêm nhé: https://bathangminh.myshopify.com")
            return events

        elif len(products) > 5:
            products = products[:5]

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

        dispatcher.utter_message(text="Hiện tại bên mình đang có những sản phẩm sau bạn tham khảo ạ:")
        dispatcher.utter_message(json_message=message)
        events.append(SlotSet(key="product_ids", value=product_ids))
        return events
