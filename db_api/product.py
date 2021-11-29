import json
import os
from dotenv import load
import shopify

load()

API_KEY = os.getenv("API_KEY")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")


def _build_query(gender, product_type, min_price, max_price, color,
                 size) -> str:
    query = ""

    if gender is not None:
        if len(query) > 0:
            query += " AND "
        query += f"tag:{gender}"

    if product_type is not None:
        if len(query) > 0:
            query += " AND "
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

    if color is not None:
        if len(query) > 0:
            query += " AND "
        if type(color) == list:
            query += " AND ".join([f"{c}" for c in color])
        if type(color) == str:
            query += f"{color}"

    if size is not None:
        if len(query) > 0:
            query += " AND "
        if type(size) == list:
            query += " AND ".join([f"{c}" for c in size])
        if type(size) == str:
            query += f"{size}"

    return query


def search_products(gender=None,
                    product_type=None,
                    min_price=None,
                    max_price=None,
                    color=None,
                    size=None):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):

        query = _build_query(gender, product_type, min_price, max_price, color,
                             size)

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
            """, {"query": query})

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
            """, {"id": product_id})

        return json.loads(response)["data"]["product"]


if __name__ == "__main__":
    # print(get_products(product_type=["quần short"], gender="nam"))
    # print(get_product_variants_by_product_id(product_id="gid://shopify/Product/7459202826454", color="Xanh dương", size="L"))
    print(search_products(product_type="áo len", color="Đỏ", size="S"))
