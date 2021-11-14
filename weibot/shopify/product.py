import json
from shopify.resources import shop
from config import APP_PASSWORD, SHOP_URL, API_VERSION
import shopify

def getProducts():
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD): 
        response = shopify.GraphQL().execute(
            """
            query getProducts {
                products(first: 50) {
                    edges {
                        cursor
                        node {
                            id
                            title

                        }
                    }
                }
            }
            """
        )

        return json.loads(response)["data"]["products"]["edges"]

if __name__ == "__main__":
    print(json.dumps(getProducts(), indent=4))