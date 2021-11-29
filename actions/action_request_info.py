from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionProductInfo(Action):
    def name(self) -> Text:
        return "action_product_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_info = {
            "id": "ms-01",
            "name": "Babydoll Bow Dress",
            "image_url": "https://cdn.shopify.com/s/files/1/0609/7046/7542/products/2015-04-08_Ashley_Look25_40663_19403_1080x.jpg?v=1636258665",
            "size": "32",
            "color": "white",
            "price": 314
        }
        elements = []
        element = {
            "title": product_info["name"],
            "image_url": product_info["image_url"],
            "buttons": [
                {
                    "type": "web_url",
                    "url": "https://bathangminh.myshopify.com/products/cape-dress-1",
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

        dispatcher.utter_message(text="Dạ mình gửi thông tin sản phẩm chi tiết ạ:")
        dispatcher.utter_message(json_message=message)

        return []
