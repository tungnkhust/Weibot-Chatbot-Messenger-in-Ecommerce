from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants
from db_api.schema import Product
from actions.utils.utils import get_product_by_object_type


class ActionRequestInfo(Action):
    def name(self) -> Text:
        return "action_request_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = []
        product = None

        pre_product_id = tracker.get_slot("product_id")
        if pre_product_id:
            pre_product = get_product_by_id(pre_product_id)
        else:
            pre_product = None

        object_types = list(
            tracker.get_latest_entity_values(entity_type="object_type"))

        if len(object_types) == 0:
            if pre_product:
                product = pre_product
            else:
                dispatcher.utter_message(text="Bạn muốn hỏi thông tin sản phẩm nào ạ")
                event.append(FollowupAction("action_suggest_product_by_entity"))
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
                    dispatcher.utter_message(text="Bạn muốn hỏi thông tin sản phẩm nào ạ")
                    event.append(FollowupAction("action_suggest_product_by_entity"))
                    return event
            else:
                # Nếu là một sp khác thì trả về sản phẩm tương ứng
                products = search_products(product_type=object_types[0])
                if products:
                    product = products[0]
                    event.append(SlotSet("object_type", object_types))
                    event.append(SlotSet("product_id", product.id))
                else:
                    pre_product_ids = tracker.get_slot("product_ids")
                    if pre_product_ids:
                        pre_products = [get_product_by_id(product_id=_id) for _id in pre_product_ids]
                    else:
                        pre_products = None

                    if pre_products:
                        _product, _score = get_product_by_object_type(object_type=object_types[0], products=pre_products)
                        if _score > 0.9:
                            product = _product
                        else:
                            dispatcher.utter_message(text="Bạn muốn hỏi thông tin sản phẩm nào ạ")
                            return event
                    else:
                        dispatcher.utter_message(text="Bạn muốn hỏi thông tin sản phẩm nào ạ")
                        return event

        if product is None:
            dispatcher.utter_message(text="Bạn muốn hỏi thông tin sản phẩm nào ạ")

        event.append(SlotSet("product_id", product.id))
        message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [product.to_info_element()]
                }
            }
        }
        dispatcher.utter_message(text="Mình gửi thông tin sản phẩm ạ:")
        dispatcher.utter_message(json_message=message)

        return event
