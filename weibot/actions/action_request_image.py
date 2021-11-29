from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionRequestImage(Action):
    def name(self) -> Text:
        return "action_request_image"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        image_url = "https://i1-vnexpress.vnecdn.net/2021/04/08/00-7617-1617852780.jpg?w=680&h=0&q=100&dpr=1&fit=crop&s=CBU5zWA2eWWfhR1Cfs-iUQ"
        message = {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url,
                    "is_reusable": True
                }
            }
        }
        dispatcher.utter_message(text="Mình gửi ảnh sản phẩm ạ:")
        dispatcher.utter_message(json_message=message)
        return []
