from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db_api.collection import get_collections


class ActionIntroProduct(Action):

    def name(self) -> Text:
        return "action_intro_product"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        events = []
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
        return events
