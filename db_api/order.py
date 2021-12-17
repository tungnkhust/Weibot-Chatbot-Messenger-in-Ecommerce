import json
from typing import Dict, List, Text
import shopify
from db_api.config import API_KEY, API_VERSION, APP_PASSWORD, SHOP_URL


def create_order(
    phone_number: Text = None,
    email: Text = None,
    address: Text = None,
    city: Text = None,
    province: Text = None,
    country: Text = None,
    zip: Text = None,
    firstname: Text = None,
    lastname: Text = None,
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
                    "email": email,
                    "shippingAddress": {
                        "address1": address,
                        "city": city,
                        "province": province,
                        "country": country,
                        "zip": zip,
                        "firstName": firstname,
                        "lastName": lastname,
                    },
                    "lineItems": items,
                }
            },
        )

    return json.loads(response)
