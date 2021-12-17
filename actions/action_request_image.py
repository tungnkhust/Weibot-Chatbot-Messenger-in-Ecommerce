import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, events
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

from actions.utils.utils import get_product_by_object_type
from db_api.product import get_product_by_id, search_products
from db_api.product_variant import search_product_variants
from db_api.product import Product


class ActionRequestPrice(Action):
    def name(self) -> Text:
        return "action_request_image"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = []
        product = None
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
        object_types = list(tracker.get_latest_entity_values("object_type"))
        colors = list(tracker.get_latest_entity_values("color"))

        if colors:
            event.append(SlotSet("color", colors[0]))

        pre_product_id = tracker.get_slot("product_id")
        if pre_product_id:
            pre_product = get_product_by_id(pre_product_id)
        else:
            pre_product = None

        # Nếu không kèm theo object_type trong request image
        if len(object_types) == 0:
            # Trả về ảnh của product trước đó nếu có hoặc hỏi lại sản phẩm nếu ko
            if pre_product:
                product = pre_product
            else:
                event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
                dispatcher.utter_message(text="Bạn muốn xem sản phẩm nào ạ")
                return event
        else:
            # Nếu có object type kèm theo, kiểm tra xem có phải đang nhắc tới sản phẩm trước đó hay ko
            object_type_level = Product.get_level_of_object_type(object_types[0])

            if object_type_level > 0:
                # Nếu có nhắc tới, thì trả ảnh sp trước đó, còn nếu là object type chung chung mà không
                # nhắc tới sp trước đó thì chuyển sang action request product
                if pre_product and pre_product.check_is_general_of_product(object_types[0]):
                    product = pre_product
                else:
                    event.append(FollowupAction("action_request_product"))
                    return event
            else:
                # Nếu là một sp khác thì trả về sản phẩm tương ứng
                product = search_products(product_type=object_types[0])[0]
                event.append(SlotSet("object_type", object_types))
                event.append(SlotSet("product_id", product.id))

        variants = search_product_variants(product_id=product.id, color=colors)
        print(colors)

        if len(variants) == 0:
            images = []
            _variants = search_product_variants(product_id=product.id)
            for variant in _variants:
                images.extend(variant.images)
            images = list(set(images))
            if len(images) == 0:
                dispatcher.utter_message(response="utter_fall_back_1")
            else:
                color_text = ", ".join(colors).strip(', ')
                dispatcher.utter_message(response=f"Dạ, hiện tại sản phẩm {product.title} không có màu {color_text}")
                dispatcher.utter_message(response=f"Bạn tham khảo một số màu khác ạ:")
                images = list(set(images))
                for img in images[:3]:
                    dispatcher.utter_message(image=img)
        else:
            images = []

            for variant in variants:
                images.extend(variant.images)

            images = list(set(images))
            dispatcher.utter_message(response="utter_send_image")
            for img in images[:3]:
                dispatcher.utter_message(image=img)

        return event
