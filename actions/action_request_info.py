from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants


class ActionRequestInfo(Action):
    def name(self) -> Text:
        return "action_request_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        events = []
        object_types = list(
            tracker.get_latest_entity_values(entity_type="object_type"))

        if len(object_types) == 0:
            product_id = tracker.get_slot("product_id")
            product = get_product_by_id(product_id)

        else:
            events.append(SlotSet(key="object_type", value=object_types))
            products = []
            for object_value in object_types:
                _products = search_products(product_type=object_value)
                products.extend(_products)

            product = products[0]

        events.append(SlotSet("product_id", product.id))
        message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [product.to_info_element()]
                }
            }
        }
        dispatcher.utter_message(json_message=message)

        return events
