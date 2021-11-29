import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api import get_products, get_product_variants
from actions.utils.product_utils import get_url


class ActionRequestProduct(Action):
    def name(self) -> Text:
        return "action_request_product"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        events = []

        object_types = tracker.get_latest_entity_values(entity_type="object_type")
        object_types = list(object_types)
        events.append(SlotSet(key="object_type", value=object_types))

        products = []
        for object_value in object_types:
            _products = get_products(product_type=object_value)
            products.extend(_products)

        if len(products) == 0:
            dispatcher.utter_message(text="Dạ, hiện tại mình không tìm thấy sản phẩm trong kho."
                                          " Bạn lên đây để tìm thêm nhé: https://bathangminh.myshopify.com")
            return events

        elif len(products) > 5:
            products = products[:5]

        elements = []
        product_ids = []
        for product in products:
            product_info = product["node"]
            title = product_info["title"]
            product_ids.append(product_info["id"])
            image_url = product_info["images"]["edges"][0]["node"]["src"]
            url = get_url(product_info)
            element = {
                "title": title,
                "image_url": image_url,
                "buttons": [
                    {
                        "type": "web_url",
                        "url": url,
                        "title": "Xem chi tiết",
                    }
                ]
            }
            elements.append(element)

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
