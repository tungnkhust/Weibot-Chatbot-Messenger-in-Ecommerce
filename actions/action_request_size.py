import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

from actions.utils.utils import get_product_by_object_type
from db_api.product import get_product_by_id, search_products
from db_api.product_variant import search_product_variants
from db_api.schema import Product


class ActionRequestSize(Action):
    def name(self) -> Text:
        return "action_request_size"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = list()
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
        product = None
        color = None
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

        if len(object_types) == 0:
            if pre_product:
                product = pre_product
            else:
                dispatcher.utter_message(text="Bạn muốn hỏi size sản phẩm nào ạ")
        else:
            # Nếu có object type kèm theo, kiểm tra xem có phải đang nhắc tới sản phẩm trước đó hay ko
            object_type_level = Product.get_level_of_object_type(object_types[0])

            if object_type_level > 0:
                # Nếu có nhắc tới, thì trả về sp trước đó, còn nếu là object type chung chung mà không
                # nhắc tới sp trước đó thì chuyển sang action request product
                if pre_product and pre_product.check_is_general_of_product(object_types[0]):
                    product = pre_product
                else:
                    dispatcher.utter_message(text="Bạn muốn hỏi size sản phẩm nào ạ")
                    return event
            else:
                # Nếu là một sp khác thì trả về sản phẩm tương ứng
                products = search_products(product_type=object_types[0])
                if products:
                    product = products[0]
                    event.append(SlotSet("object_type", object_types))
                    event.append(SlotSet("product_id", product.id))

                else:
                    dispatcher.utter_message(text="Bạn muốn hỏi size sản phẩm nào ạ")
                    return event

        if product is None:
            dispatcher.utter_message(text="Bạn muốn hỏi size sản phẩm nào ạ")
            return event

        variants = search_product_variants(product_id=product.id, color=color)

        if len(variants) == 0:
            dispatcher.utter_message(text="Bạn muốn hỏi size sản phẩm nào ạ")
        else:
            sizes = []
            for variant in variants:
                sizes.append(variant.size)
            sizes = list(set(sizes))

            if len(sizes) == 0:
                dispatcher.utter_message(text="Bạn muốn hỏi size sản phẩm nào ạ")
            else:
                sizes_text = ", ".join(sizes).strip(', ')
                if color:
                    text = f"Sản phẩm *{product.title}* màu *{color}* đang còn size: *{sizes_text}* ạ"
                else:
                    text = f"Sản phẩm *{product.title}* đang có size: *{sizes_text}* ạ"
                dispatcher.utter_message(text=text)

        return event
