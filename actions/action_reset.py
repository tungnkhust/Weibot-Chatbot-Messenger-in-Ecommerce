from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionGreet(Action):

    def name(self) -> Text:
        return "action_reset_slots"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slots = [
            SlotSet(key="greeted", value=False),
            SlotSet(key="product_ids", value=[]),
            SlotSet(key="product_id", value=None),
            SlotSet(key="object_type", value=None),
            SlotSet(key="color", value=None),
            SlotSet(key="size", value=None),
            SlotSet(key="gender", value=None),
            SlotSet(key="price", value=None)
        ]

        return slots
