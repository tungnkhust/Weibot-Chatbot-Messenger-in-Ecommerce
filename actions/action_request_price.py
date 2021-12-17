import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

from actions.utils.utils import get_product_by_object_type
from db_api.product import get_product_by_id, search_products
from db_api.product_variant import search_product_variants
from db_api.schema import Product


class ActionRequestPrice(Action):
    def name(self) -> Text:
        return "action_request_price"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = []
        product = None
        color = None
        size = None
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
        pre_product_id = tracker.get_slot("product_id")
        if pre_product_id:
            pre_product = get_product_by_id(pre_product_id)
        else:
            pre_product = None

        object_types = list(tracker.get_latest_entity_values("object_type"))
        colors = list(tracker.get_latest_entity_values("color"))
        if colors:
            color = colors[0]
            event.append(SlotSet("color", color))

        sizes = list(tracker.get_latest_entity_values("size"))
        if sizes:
            size = sizes[0]
            event.append(SlotSet("size", size))

        if len(object_types) == 0:
            if pre_product:
                product = pre_product
            else:
                dispatcher.utter_message(text="Bạn muốn hỏi giá sản phẩm nào ạ")
                return event
        else:
            # Nếu có object type kèm theo, kiểm tra xem có phải đang nhắc tới sản phẩm trước đó hay ko
            object_type_level = Product.get_level_of_object_type(object_types[0])

            if object_type_level > 0:
                # Nếu có nhắc tới, thì trả về sp trước đó, còn nếu là object type chung chung mà không
                # nhắc tới sp trước đó thì chuyển sang action request product
                if pre_product and pre_product.check_is_general_of_product(object_types[0]):
                    product = pre_product
                else:
                    dispatcher.utter_message(text="Bạn muốn hỏi giá sản phẩm nào ạ")
                    return event
            else:
                # Nếu là một sp khác thì trả về sản phẩm tương ứng
                products = search_products(product_type=object_types[0])
                if products:
                    product = products[0]
                    event.append(SlotSet("object_type", object_types))
                    event.append(SlotSet("product_id", product.id))

                else:
                    dispatcher.utter_message(text="Bạn muốn hỏi giá sản phẩm nào ạ")
                    return event

        if product is None:
            dispatcher.utter_message(text="Bạn muốn hỏi giá sản phẩm nào ạ")
            return event

        variants = search_product_variants(product_id=product.id, size=size, color=color)

        if len(variants) == 0:
            dispatcher.utter_message(text="Bạn muốn hỏi giá sản phẩm nào ạ")
        else:
            elements = []
            _colors = []
            for variant in variants:
                if variant.color not in _colors:
                    elements.append(variant.to_messenger_element())
                    _colors.append(variant.color)

            if elements:
                message = {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": elements
                        }
                    }
                }
                dispatcher.utter_message(text=f"Sản phẩm {product.title} có giá theo màu sắc và kích thước như sau:")
                dispatcher.utter_message(json_message=message)
            else:
                dispatcher.utter_message(text="Bạn muốn hỏi giá sản phẩm nào ạ")
        return event
