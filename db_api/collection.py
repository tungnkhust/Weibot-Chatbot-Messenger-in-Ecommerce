import json
import shopify
from db_api.config import API_KEY, API_VERSION, APP_PASSWORD, SHOP_URL


def get_collections():
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        response = shopify.GraphQL().execute("""
            {
                collections(first: 30, query:"-title:Nam AND -title:Nữ AND -title:'Còn hàng'") {
                    edges {
                        node {
                            id
                            title
                        }
                    }
                }
            }
            """)

        return json.loads(response)["data"]["collections"]["edges"]