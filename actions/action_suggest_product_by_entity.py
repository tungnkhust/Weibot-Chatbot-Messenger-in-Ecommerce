import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.product import get_product_by_id, search_products
from actions.utils.product_utils import get_url
import random


class ActionSuggestProductByEntity(Action):
    def name(self) -> Text:
        return "action_suggest_product_by_entity"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event = []

        gender = list(tracker.get_latest_entity_values(entity_type="gender"))
        if len(set(gender)) != 1:
            gender = None
        else:
            gender = gender[0]
            event.append(SlotSet(key="gender", value=gender))

        color = list(tracker.get_latest_entity_values(entity_type="color"))
        if len(set(color)) == 0:
            color = None
        else:
            color = color[0]
            event.append(SlotSet(key="color", value=color))

        products = search_products(gender=gender, color=color)

        if len(products) == 0:
            dispatcher.utter_message(text="Bạn lên đây để tìm thêm nhé: https://bathangminh.myshopify.com")
            return event

        elif len(products) > 10:
            random.shuffle(products)
            products = products[:10]

        elements = []
        product_ids = []
        for product in products:
            element = product.to_info_element()
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
        if (gender is not None) and (color is not None):
            dispatcher.utter_message(
                text=f"Bên mình hiện có một số sản phẩm cho *{gender}* màu *{color}* sau, bạn tham khảo ạ")
        elif gender:
            dispatcher.utter_message(
                text=f"Bên mình hiện có một số sản phẩm cho *{gender}* sau, bạn tham khảo ạ")
        elif color:
            dispatcher.utter_message(
                text=f"Bên mình hiện có một số sản phẩm màu *{color}* sau, bạn tham khảo ạ")
        else:
            dispatcher.utter_message(
                text=f"Bên mình hiện có một số sản phẩm sau, bạn tham khảo ạ")

        dispatcher.utter_message(json_message=message)
        event.append(SlotSet(key="product_ids", value=product_ids))
        event.append(SlotSet(key="product_id", value=None))
        event.append(SlotSet("request_no_has", None))
        return event
