from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants, get_product_variant_by_id
from db_api.schema import Product
from actions.utils.utils import get_generic_message


class ActionRequestOrder(Action):
    def name(self) -> Text:
        return "action_request_order"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = []
        product = None
        product_other = False
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
        event.append(SlotSet("system_act", self.name()))

        pre_product_id = tracker.get_slot("product_id")
        if pre_product_id:
            pre_product = get_product_by_id(pre_product_id)
        else:
            pre_product = None

        object_types = list(tracker.get_latest_entity_values(entity_type="object_type"))

        colors = list(tracker.get_latest_entity_values(entity_type="color"))
        if colors:
            color = colors[0]
        else:
            color = tracker.get_slot("color")

        sizes = list(tracker.get_latest_entity_values(entity_type="size"))
        if sizes:
            size = sizes[0]
        else:
            size = tracker.get_slot("size")

        if len(object_types) == 0:
            if pre_product:
                product = pre_product
            else:
                dispatcher.utter_message(text="Bạn muốn hỏi mua sản phẩm nào ạ")
                event.append(FollowupAction("action_suggest_product_by_entity"))
        else:
            # Nếu có object type kèm theo, kiểm tra xem có phải đang nhắc tới sản phẩm trước đó hay ko
            object_type_level = Product.get_level_of_object_type(object_types[0])

            if object_type_level > 0:
                # Nếu có nhắc tới, thì trả về màu sp trước đó, còn nếu là object type chung chung mà không
                # nhắc tới sp trước đó thì chuyển sang action request product
                if pre_product and pre_product.check_is_general_of_product(object_types[0]):
                    product = pre_product
                else:
                    dispatcher.utter_message(text="Bạn muốn mua sản phẩm nào ạ")
                    event.append(FollowupAction("action_request_product"))
                    return event
            else:
                # Nếu là một sp khác thì trả về sản phẩm tương ứng
                products = search_products(product_type=object_types[0], size=size, color=color)
                if products:
                    product = products[0]
                    event.append(SlotSet("object_type", object_types))
                    event.append(SlotSet("product_id", product.id))
                    product_other = True
                else:
                    dispatcher.utter_message(text="Bạn muốn mua sản phẩm nào ạ")
                    return event

        if product is None:
            dispatcher.utter_message(text="Bạn muốn mua sản phẩm nào ạ")
            return event

        product_colors = [c.lower() for c in product.colors.copy()]
        product_sizes = [s.lower() for s in product.sizes.copy()]

        event.append(SlotSet("color", color))
        event.append(SlotSet("size", size))

        if product_other:
            dispatcher.utter_message(text="Có phải bạn hỏi mua sản phẩm này không ạ")
            message = get_generic_message([product.to_info_element()])
            dispatcher.utter_message(json_message=message)
            return event
        else:
            if color is None and size is None:
                dispatcher.utter_message(text="Bạn muốn lấy màu và size nào ạ")
            elif color is None:
                dispatcher.utter_message(text="Bạn muốn lấy màu nào ạ")
            elif size is None:
                dispatcher.utter_message(text="Bạn muốn lấy size nào ạ")
            else:
                if color not in product_colors:
                    product_colors_text = ", ".join(product_colors).strip(", ")
                    dispatcher.utter_message(text=f"Sản phẩm {product.title} không có màu *{color}* bạn chọn màu khác"
                                                  f" được không ạ: {product_colors_text}")
                    return event

                if size not in product_sizes:
                    product_sizes_text = ", ".join(product_sizes).strip(", ")
                    dispatcher.utter_message(text=f"Sản phẩm {product.title} không có size *{size}* bạn chọn size khác"
                                                  f" được không ạ: {product_sizes_text}")
                    return event

                variants = search_product_variants(product_id=product.id, color=colors,
                                                   size=sizes, handle=product.handle)

                if len(variants) == 0:
                    dispatcher.utter_message(text=f"Hiện tại sản phẩm {product.title} màu {color} size {size} đang không có"
                                                  f"\nBạn chọn màu hoặc size khác giúp mình với ạ.")
                    return event

                variant_ids = [variant.id for variant in variants]
                event.append(SlotSet("variant_ids", variant_ids))
                elements = [variant.to_messenger_element() for variant in variants]
                message = get_generic_message(elements)

                confirmed_order = tracker.get_slot("confirmed_order")

                if confirmed_order:
                    event.append(FollowupAction("action_request_user_info"))
                    return event

                elif confirmed_order is False:
                    dispatcher.utter_message(text="Bạn báo lại thông tin sản phẩm cần mua với ạ")
                    return event
                dispatcher.utter_message(text="Mình gửi danh sách các sản phẩm bạn chọn. Bạn xác nhận giúp mình đúng"
                                              " chưa ạ")
                dispatcher.utter_message(json_message=message)

        return event
