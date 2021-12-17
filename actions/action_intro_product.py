from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, events
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.collection import get_collections


class ActionIntroProduct(Action):

    def name(self) -> Text:
        return "action_intro_product"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = list()
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))

        object_types = list(tracker.get_latest_entity_values("object_type"))
        if object_types:
            return [
                SlotSet("object_type", object_types),
                events.FollowupAction("action_request_product")
            ]

        gender = list(tracker.get_latest_entity_values("gender"))
        if gender:
            return [
                events.FollowupAction("action_suggest_product_by_entity")
            ]

        color = list(tracker.get_latest_entity_values("color"))
        if color:
            return [
                events.FollowupAction("action_suggest_product_by_entity")
            ]

        nodes = get_collections()
        products = []
        for node in nodes:
            products.append(node["node"]["title"])

        text = f"Bên mình kinh doanh các mặt hàng về thời trang bao gồm:\n"
        text += "- " + ", ".join(products[:3]).strip(', ') + "\n"
        text += "- " + ", ".join(products[3:6]).strip(', ') + "\n"
        text += "- " + ", ".join(products[6:9]).strip(', ') + "\n"
        text += "- " + ", ".join(products[9:]).strip(', ')
        dispatcher.utter_message(text=text)

        return event
