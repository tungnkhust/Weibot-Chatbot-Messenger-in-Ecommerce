import json
import shopify
from typing import Text, Union, List, Dict, Optional
from db_api.config import API_KEY, API_VERSION, APP_PASSWORD, SHOP_URL
from db_api.schema import Product


def _build_query(
        gender: Optional[Text] = None,
        product_type: Optional[Text] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        color: Optional[Text] = None,
        size: Optional[Text] = None
) -> str:
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


def search_products(
        gender: Optional[Text] = None,
        product_type: Optional[Text] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        color: Optional[Text] = None,
        size: Optional[Union[int, Text]] = None
):

    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):

        query = _build_query(gender, product_type, min_price, max_price, color,
                             size)

        response = shopify.GraphQL().execute(
            """
            query($query: String) {
                products(first: 20, query: $query) {
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
        nodes = json.loads(response)["data"]["products"]["edges"]

        products = []
        for node in nodes:
            products.append(Product.from_dict(node))

        return products


def get_product_by_id(
        product_id: Text
):
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

        node = json.loads(response)["data"]["product"]
        return Product.from_dict(node)

