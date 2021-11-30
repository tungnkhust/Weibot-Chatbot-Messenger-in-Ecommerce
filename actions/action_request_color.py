from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.product import search_products


class ActionRequestColor(Action):
    def name(self) -> Text:
        return "action_request_color"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        events = []
        object_types = list(
            tracker.get_latest_entity_values(entity_type="object_type"))
        if len(object_types) == 0:
            object_types = tracker.get_slot("object_type")
        events.append(SlotSet(key="object_type", value=object_types))

        products = []
        for object_value in object_types:
            _products = search_products(product_type=object_value)
            products.extend(_products)

        if len(products) == 0:
            dispatcher.utter_message(
                text="Dạ, hiện tại mình không tìm thấy sản phẩm trong kho."
                " Bạn lên đây để tìm thêm nhé: https://bathangminh.myshopify.com"
            )
            return events

        colors = []
        for product in products:
            product_info = product["node"]
            options = product_info["options"]
            for option in options:
                if option["name"] == "Màu sắc":
                    colors.extend(option["values"])

        colors = set(colors)
        color_text = ", ".join(colors).strip(',')
        dispatcher.utter_message(
            text=f"Dạ, shop mình đang còn màu: {color_text} ạ")
        return events
