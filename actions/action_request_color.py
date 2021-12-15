from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants, get_product_variant_by_id
from db_api.schema import Product


def get_color_product(product_id):
    variants = search_product_variants(product_id)
    colors = []
    for variant in variants:
        if variant.color and variant.color not in colors:
            colors.append(variant.color)
    return colors


class ActionRequestColor(Action):
    def name(self) -> Text:
        return "action_request_color"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = []
        product = None
        product_other = False

        pre_product_id = tracker.get_slot("product_id")
        if pre_product_id:
            pre_product = get_product_by_id(pre_product_id)
        else:
            pre_product = None

        object_types = list(tracker.get_latest_entity_values(entity_type="object_type"))

        if len(object_types) == 0:
            if pre_product:
                product = pre_product
            else:
                dispatcher.utter_message(text="Bạn muốn xem màu sản phẩm nào ạ")
        else:
            # Nếu có object type kèm theo, kiểm tra xem có phải đang nhắc tới sản phẩm trước đó hay ko
            object_type_level = Product.get_level_of_object_type(object_types[0])

            if object_type_level > 0:
                # Nếu có nhắc tới, thì trả về màu sp trước đó, còn nếu là object type chung chung mà không
                # nhắc tới sp trước đó thì chuyển sang action request product
                if pre_product and pre_product.check_is_general_of_product(object_types[0]):
                    product = pre_product
                else:
                    dispatcher.utter_message(text="Có phải bạn đang tìm kiếm sản phẩm không ạ")
                    event.append(FollowupAction("action_request_product"))
                    return event
            else:
                # Nếu là một sp khác thì trả về sản phẩm tương ứng
                products = search_products(product_type=object_types[0])
                if products:
                    product = products[0]
                    event.append(SlotSet("object_type", object_types))
                    event.append(SlotSet("product_id", product.id))
                    product_other = True
                else:
                    dispatcher.utter_message(text="Bạn muốn hỏi màu sản phẩm nào ạ")
                    return event

        if product is None:
            dispatcher.utter_message(text="Bạn muốn hỏi màu sản phẩm nào ạ")
            return event

        colors = get_color_product(product.id)
        if len(colors) == 0:
            dispatcher.utter_message(response="utter_fall_back_1")
        else:
            color_text = ", ".join(colors).strip(',')
            text = f"Dạ, Sản phâm {product.title} bên mình đang còn màu: {color_text} ạ"
            dispatcher.utter_message(text)
            if product_other:
                variant_dict = {}
                for color in colors:
                    variants = search_product_variants(product_id=product.id, color=color)
                    if variants:
                        variant_dict[color] = variants[0]
                elements = []
                for color, variant in variant_dict.items():
                    element = variant.to_messenger_element()
                    elements.append(element)

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
                    dispatcher.utter_message(json_message=message)
        return event
