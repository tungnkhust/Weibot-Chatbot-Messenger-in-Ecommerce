from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = []
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))

        greeted = tracker.get_slot("greeted")

        if greeted:
            dispatcher.utter_message(response='utter_greet_1')
        else:
            dispatcher.utter_message(response='utter_greet_0')
            event.append(SlotSet(key="greeted", value=True))

        return event
