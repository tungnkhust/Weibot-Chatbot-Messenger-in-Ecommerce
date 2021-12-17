from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import search_product_variants, get_product_variant_by_id
from db_api.schema import Product


class ActionRequestUserInfo(Action):
    def name(self) -> Text:
        return "action_request_user_info"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event = list()
        event.append(SlotSet("intent", tracker.get_intent_of_latest_message()))
        event.append(SlotSet("system_act", self.name()))

        variant_ids = tracker.get_slot("variant_ids")
        if variant_ids is None or len(variant_ids) == 0:
            event.append(FollowupAction("action_request_order"))
            return event

        user_name = [tracker.get_latest_entity_values("name")]
        intent = tracker.get_intent_of_latest_message()

        if "inform" not in intent:
            dispatcher.utter_message(text="Dạ, Vui lòng cho mình xin tên đầy đủ của bạn được không ạ?")
            return event

        if user_name:
            event.append(SlotSet("user_name", user_name))
        else:
            dispatcher.utter_message(text="Cho mình xin tên đầy đủ của bạn ạ.")

        phone_number = [tracker.get_latest_entity_values("phone_number")]
        if phone_number:
            event.append(SlotSet("phone_number", phone_number))
        else:
            dispatcher.utter_message(text="Cho mình xin số điện thoại của bạn ạ.")
            return event

        address = [tracker.get_latest_entity_values("address")]
        if address:
            event.append(SlotSet("address", address))
        else:
            dispatcher.utter_message(text="Bạn ở số nhà bao nhiêu và đường phố nào ạ")
            return event

        district = [tracker.get_latest_entity_values("district")]
        if district:
            event.append(SlotSet("district", district))
        else:
            dispatcher.utter_message(text="Bạn ở quận (huyện) nào ạ")
            return event

        province = [tracker.get_latest_entity_values("province")]
        if province:
            event.append(SlotSet("province", province))
        else:
            dispatcher.utter_message(text="Bạn ở tỉnh (thành phố) nào ạ")
            return event

        event.append(FollowupAction("action_confirm_checkout"))
        return event
