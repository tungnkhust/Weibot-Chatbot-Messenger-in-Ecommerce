import json
from config import APP_PASSWORD, SHOP_URL, API_VERSION
import shopify

def getCollections():
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        response = shopify.GraphQL().execute(
            """
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
            """
        )

        return json.loads(response)["data"]["collections"]["edges"]

if __name__ == "__main__":
    print(getCollections())