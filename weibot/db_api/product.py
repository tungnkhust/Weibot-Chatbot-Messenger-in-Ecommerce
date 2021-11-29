import json
from db_api.config import APP_PASSWORD, SHOP_URL, API_VERSION
import shopify


def _build_query(sex, product_type, min_price, max_price) -> str:
    query = ""

    if sex is not None:
        if len(query) > 0:
            query += " AND "
        query += f"tag:{sex}"
    
    if product_type is not None:
        if len(query) > 0:
            query += " AND "
        print(type(product_type))
        if type(product_type) == list:
            query += " AND ".join([f"tag:{pd}" for pd in product_type])   
        if type(product_type) == str:
            query += f"tag:{product_type}"

    if min_price is not None:
        if len(query) > 0:
            query += " AND "
        query += f"price:>={min_price}"

    if max_price is not None:
        if len(query) > 0:
            query += " AND "
        query += f"price:<={max_price}"
    
    return query


def get_product_variants():
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD): 
        response = shopify.GraphQL().execute(
            """
            {
                productVariants(first: 10) {
                    edges {
                        node {
                            id
                            displayName
                            inventoryQuantity
                            price
                            selectedOptions {
                                name
                                value
                            }
                            product {
                                handle
                                title
                                vendor
                                description
                                productType
                                tags
                                images(first: 1) {
                                    edges {
                                        node {
                                            src
                                        }
                                    }
                                }
                            }
                            image {
                                src
                                altText
                            }
                        }
                    }
                }
            }
            """
        )

        return json.loads(response)["data"]["productVariants"]["edges"]


def get_products(sex=None, product_type=None, min_price=None, max_price=None):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        
        query = _build_query(sex, product_type, min_price, max_price)
        
        response = shopify.GraphQL().execute(
            f"""
            {{
                products(first: 5, query:"{query}") {{
                    edges {{
                        node {{
                            id
                            handle
                            title
                            tags
                            totalInventory
                            productType
                            description
                            priceRangeV2 {{
                                minVariantPrice {{
                                    amount
                                }}
                                maxVariantPrice {{
                                    amount
                                }}
                            }}
                            options(first: 3) {{
                                name
                                values
                            }}
                            vendor
                            images(first: 1) {{
                                edges {{
                                    node {{
                                        src
                                        altText
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
            """
        )
        
        return json.loads(response)["data"]["products"]["edges"]
