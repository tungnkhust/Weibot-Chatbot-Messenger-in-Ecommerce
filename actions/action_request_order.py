from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants, get_product_variant_by_id
from db_api.schema import Product
from actions.utils.utils import get_generic_message
from db_api.order import create_order

from actions.utils.utils import check_in_list


def get_draft_order(variant_ids):
    items = []
    for var_id in variant_ids:
        items.append({
            "variantId": var_id,
            "quantity": 1
        })
    output = create_order(items)
    order_url = output["data"]["draftOrderCreate"]["draftOrder"]["invoiceUrl"]
    return order_url


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
                dispatcher.utter_message(text="B???n mu???n h???i mua s???n ph???m n??o ???")
                event.append(FollowupAction("action_suggest_product_by_entity"))
        else:
            # N???u c?? object type k??m theo, ki???m tra xem c?? ph???i ??ang nh???c t???i s???n ph???m tr?????c ???? hay ko
            object_type_level = Product.get_level_of_object_type(object_types[0])

            if object_type_level > 0:
                # N???u c?? nh???c t???i, th?? tr??? v??? m??u sp tr?????c ????, c??n n???u l?? object type chung chung m?? kh??ng
                # nh???c t???i sp tr?????c ???? th?? chuy???n sang action request product
                if pre_product and pre_product.check_is_general_of_product(object_types[0]):
                    product = pre_product
                else:
                    dispatcher.utter_message(text="B???n mu???n mua s???n ph???m n??o ???")
                    event.append(FollowupAction("action_request_product"))
                    return event
            else:
                # N???u l?? m???t sp kh??c th?? tr??? v??? s???n ph???m t????ng ???ng
                products = search_products(product_type=object_types[0], size=size, color=color)
                if products:
                    product = products[0]
                    event.append(SlotSet("object_type", object_types))
                    event.append(SlotSet("product_id", product.id))
                    product_other = True
                else:
                    dispatcher.utter_message(text="B???n mu???n mua s???n ph???m n??o ???")
                    return event

        if product is None:
            dispatcher.utter_message(text="B???n mu???n mua s???n ph???m n??o ???")
            return event

        product_colors = [c.lower() for c in product.colors.copy()]
        product_sizes = [s.lower() for s in product.sizes.copy()]

        event.append(SlotSet("color", color))
        event.append(SlotSet("size", size))
        tracker.add_slots(event)

        if product_other:
            dispatcher.utter_message(text="C?? ph???i b???n h???i mua s???n ph???m n??y ????ng kh??ng ???")
            message = get_generic_message([product.to_info_element()])
            dispatcher.utter_message(json_message=message)
            return event
        else:
            if color is None and size is None:
                dispatcher.utter_message(text="B???n mu???n l???y m??u v?? size n??o ???")
            elif color is None:
                dispatcher.utter_message(text="B???n mu???n l???y m??u n??o ???")
            elif size is None:
                dispatcher.utter_message(text="B???n mu???n l???y size n??o ???")
            else:
                if check_in_list(color, product_colors) is False:
                    product_colors_text = ", ".join(product_colors).strip(", ")
                    dispatcher.utter_message(text=f"S???n ph???m {product.title} kh??ng c?? m??u *{color}* b???n ch???n m??u kh??c"
                                                  f" ???????c kh??ng ???: {product_colors_text}")
                    return event

                if check_in_list(size, product_sizes) is False:
                    product_sizes_text = ", ".join(product_sizes).strip(", ")
                    dispatcher.utter_message(text=f"S???n ph???m {product.title} kh??ng c?? size *{size}* b???n ch???n size kh??c"
                                                  f" ???????c kh??ng ???: {product_sizes_text}")
                    return event

                variants = search_product_variants(product_id=product.id, color=colors,
                                                   size=sizes, handle=product.handle)

                if len(variants) == 0:
                    dispatcher.utter_message(text=f"Hi???n t???i s???n ph???m {product.title} m??u {color} size {size} ??ang kh??ng c??"
                                                  f"\nB???n ch???n m??u ho???c size kh??c gi??p m??nh v???i ???.")
                    return event

                dispatcher.utter_message("M??nh g???i danh s??ch s???n ph???m b???n ?????t mua:")
                variant_ids = [variant.id for variant in variants]
                order_url = get_draft_order(variant_ids)
                elements = [variant.to_messenger_generic() for variant in variants]
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
                message = {
                    "attachment": {
                          "type": "template",
                          "payload": {
                                "template_type": "button",
                                "text": "???n *?????t H??ng* ????? mua",
                                "buttons": [
                                  {
                                    "type": "web_url",
                                    "url": order_url,
                                    "title": "?????t H??ng",
                                    "webview_height_ratio": "full"
                                  }
                                ]
                              }
                        }
                }
                dispatcher.utter_message(json_message=message)

        return event
