from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product_variant import get_product_variant_by_id
from db_api.order import create_order
from db_api.schema import Variant


class ActionConfirmCheckout(Action):

    def name(self) -> Text:
        return "action_confirm_checkout"

    async def _create_order(
            self,
            variants: List[Variant],
            user_name,
            phone_number=None,
            address=None,
            district=None,
            province=None,
            country="Việt Nam",
            zipcode="100000"
    ):
        items = []
        for variant in variants:
            items.append({"variantId": variant.id, "quantity": 1})
        try:
            res = create_order(
                phone_number=phone_number,
                address=address,
                province=district,
                city=province,
                country=country,
                lastname="",
                firstname=user_name,
                zip=zipcode,
                items=items
            )
            if "data" in res:
                if "draftOrderCreate" in res["data"]:
                    if "draftOrder" in res["data"]["draftOrderCreate"]:
                        order_id = res["data"]["draftOrderCreate"]["draftOrder"]["id"]
                        return order_id
        except:
            print("---> Create order fail")
            return None

        print("---> Create order fail")
        return None

    async def process_order_request(
            self,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ):
        pass

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event = list()

        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
        event.append(SlotSet("system_act", self.name()))

        address = tracker.get_slot("address")
        if address is None:
            event.append(FollowupAction("action_request_user_info"))

        ward = tracker.get_slot("ward")
        if ward:
            address += " " + ward

        district = tracker.get_slot("district")
        if district is None:
            event.append(FollowupAction("action_request_user_info"))

        province = tracker.get_slot("province")
        if province is None:
            event.append(FollowupAction("action_request_user_info"))

        phone_number = tracker.get_slot("phone_number")
        if phone_number is None:
            event.append(FollowupAction("action_request_user_info"))

        user_name = tracker.get_slot("user_name")
        if user_name is None:
            event.append(FollowupAction("action_request_user_info"))

        variant_ids = tracker.get_slot("variant_ids")
        variants = [get_product_variant_by_id(variant_id) for variant_id in variant_ids]

        confirmed_checkout = tracker.get_slot("confirmed_checkout")

        if confirmed_checkout:
            order_id = await self._create_order(
                address=address,
                district=district,
                province=province,
                phone_number=phone_number,
                user_name=user_name,
                variants=variants
            )
            if order_id:
                dispatcher.utter_message(text="Đơn hàng đã được tạo thành công. Bạn có mua thêm gì nữa không ạ")
                order_ids = tracker.get_slot("order_ids")
                order_ids.append(order_id)
                event.append(SlotSet("order_ids", order_ids))
                event.append(SlotSet("system_act", "ask_buy_more"))
                event.append(FollowupAction("action_reset_slots"))
                return event

            else:
                dispatcher.utter_message(text="Đơn hàng được tạo không thành công, rất xin lỗi vì sự cố này ạ.\n"
                                              " Bạn liên hệ qua số điện thoại 098765888 để được nhân viên bên mình"
                                              "đặt hàng trực tiếp ạ")
                event.append(FollowupAction("action_reset_slots"))
                return event

        elements = []
        for variant in variants:
            element = {
                            "title": variant.display_name,
                            "subtitle": f"Màu: {variant.color} - Size: {variant.size}",
                            "quantity": 1,
                            "price": variant.price,
                            "currency": "VND",
                            "image_url": variant.images[0]
                        }
            elements.append(element)

        message = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "receipt",
                    "currency": "VND",
                    "address": {
                        "street_1": address,
                        "city": district,
                        "state": province,
                        "country": "Việt Nam"
                    },
                    "summary": {
                        "shipping_cost": "30000",
                        "total_cost": "1000000"
                    },
                    "elements": elements
                }
            }
        }
        dispatcher.utter_message(text="Mình gửi bạn đơn hàng, bạn xác nhận để chốt đơn ạ.")
        dispatcher.utter_message(json_message=message)

        return event
