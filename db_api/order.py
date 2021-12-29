import json
from typing import Dict, List, Text
import shopify
from db_api.config import API_KEY, API_VERSION, APP_PASSWORD, SHOP_URL


def create_order(
    items: List[Dict[Text, int]] = None,
):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        response = shopify.GraphQL().execute(
            """
        mutation draftOrderCreate($input: DraftOrderInput!) {
            draftOrderCreate(input: $input) {
                draftOrder {
                    # DraftOrder fields
                    id
                    invoiceUrl
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """,
            variables={
                "input": {
                    "note": "chatbot",
                    "lineItems": items,
                }
            },
        )

    return json.loads(response)
