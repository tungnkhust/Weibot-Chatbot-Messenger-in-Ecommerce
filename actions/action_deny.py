from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction


class ActionDeny(Action):

    def name(self) -> Text:
        return "action_deny"

    async def process_order_request(
            self,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ):
        pass

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event = []

        pre_system_act = tracker.get_slot("system_act")
        if pre_system_act == "action_request_order":
            event.append(SlotSet("confirmed_order", False))
            event.append(FollowupAction("action_request_order"))
            return event

        if pre_system_act == "action_confirm_checkout":
            event.append(SlotSet("confirmed_checkout", False))
            event.append(FollowupAction("action_confirm_checkout"))
            return event

        if pre_system_act == "ask_buy_more":
            dispatcher.utter_message(text="Dạ bạn chuyển khoản qua số tài khoản sau để thanh toán giúp mình nha ạ:\n"
                                          "- STK: 1240201312626\n"
                                          "- Ngân hàng: Agriank chi nhánh Hoàng Mai\n"
                                          "- Tên người nhận: Đăng Tuấn Tùng\n"
                                          "- Hoặc Momo: 098786868")
            return event

        return event
