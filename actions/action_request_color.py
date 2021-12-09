from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants


def get_color_product(product_id):
    variants = search_product_variants(product_id)
    colors = []
    for variant in variants:
        if variant.color and variant.color not in colors:
            colors.append(variant.color)
    return colors


class ActionRequestColor(Action):
    def name(self) -> Text:
        return "action_request_color"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        events = []
        object_types = list(
            tracker.get_latest_entity_values(entity_type="object_type"))

        if len(object_types) == 0:
            product_id = tracker.get_slot("product_id")
            product = get_product_by_id(product_id)
            colors = get_color_product(product_id)
            colors = set(colors)
            color_text = ", ".join(colors).strip(',')
            text = f"Dạ, Sản phẩm *{product.title}* bên mình đang còn màu: {color_text} ạ"
        else:
            events.append(SlotSet(key="object_type", value=object_types))
            products = []
            for object_value in object_types:
                _products = search_products(product_type=object_value)
                products.extend(_products)

            product = products[0]
            events.append(SlotSet("product_id", product.id))

            colors = get_color_product(product.id)
            color_text = ", ".join(colors).strip(',')
            text = f"Dạ, bên mình đang còn màu: {color_text} ạ"

        if len(colors) == 0:
            dispatcher.utter_message(response="utter_fall_back_1")
        else:
            dispatcher.utter_message(text)

        return events
