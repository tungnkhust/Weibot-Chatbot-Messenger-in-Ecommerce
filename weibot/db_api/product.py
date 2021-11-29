import json
from config import APP_PASSWORD, SHOP_URL, API_VERSION
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
                                id
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

def get_product_variant_by_id(variant_id):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        response = shopify.GraphQL().execute(
            """
            query ($id: ID!) {
                productVariant(id: $id) {
                    id
                    displayName
                    inventoryQuantity
                    price
                    selectedOptions {
                        name
                        value
                    }
                    product {
                        id
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
            """,
            {
                "id": variant_id
            }
        )

        return json.loads(response)["data"]["productVariant"]

def get_products(sex=None, product_type=None, min_price=None, max_price=None):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        
        query = _build_query(sex, product_type, min_price, max_price)
        
        response = shopify.GraphQL().execute(
            """
            query($query: String) {
                products(first: 5, query: $query) {
                    edges {
                        node {
                            id
                            handle
                            title
                            tags
                            totalInventory
                            productType
                            description
                            priceRangeV2 {
                                minVariantPrice {
                                    amount
                                }
                                maxVariantPrice {
                                    amount
                                }
                            }
                            options(first: 3) {
                                name
                                values
                            }
                            vendor
                            images(first: 1) {
                                edges {
                                    node {
                                        src
                                        altText
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """,
            {
                "query": query
            }
        )
        
        return json.loads(response)["data"]["products"]["edges"]

def get_product_by_id(product_id):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        response = shopify.GraphQL().execute(
            """
            query ($id: ID!) {
                product(id: $id) {
                    id
                    handle
                    title
                    tags
                    totalInventory
                    productType
                    description
                    priceRangeV2 {
                        minVariantPrice {
                            amount
                        }
                        maxVariantPrice {
                            amount
                        }
                    }
                    options(first: 3) {
                        name
                        values
                    }
                    vendor
                    images(first: 1) {
                        edges {
                            node {
                                src
                                altText
                            }
                        }
                    }
                }
            }
            """,
            {
                "id": product_id
            }
        )

        return json.loads(response)["data"]["product"]

if __name__ == "__main__":
    print(get_products(product_type=["quần short"], sex="nam"))
