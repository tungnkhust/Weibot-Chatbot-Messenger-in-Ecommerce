import json
import shopify
import os
from dotenv import load

load()

API_KEY = os.getenv("API_KEY")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")


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


if __name__ == "__main__":
    print(get_collections())