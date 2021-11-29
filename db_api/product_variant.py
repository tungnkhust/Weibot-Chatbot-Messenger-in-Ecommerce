import json
import os
from dotenv import load
import shopify

load()

API_KEY = os.getenv("API_KEY")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")


def search_product_variants(product_id,
                            color=None,
                            size=None,
                            min_price=None,
                            max_price=None):
    with shopify.Session.temp(SHOP_URL, API_VERSION, APP_PASSWORD):
        response = shopify.GraphQL().execute(
            """
            query ($id: ID!) {
                product(id: $id) {
                    variants(first: 100) {
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
                                image {
                                    src
                                    altText
                                }
                            }
                        }
                    }
                }
            }
            """, {"id": product_id})

        variants = json.loads(response)["data"]["product"]["variants"]["edges"]

        to_removes = []

        if color != None:
            for (idx, variant) in enumerate(variants):
                if variant["node"]["selectedOptions"][0][
                        "name"] == "Màu sắc" and variant["node"][
                            "selectedOptions"][0]["value"] == color:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        if size != None:
            for (idx, variant) in enumerate(variants):
                if variant["node"]["selectedOptions"][1][
                        "name"] == "Kích cỡ" and variant["node"][
                            "selectedOptions"][1]["value"] == size:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        if min_price != None:
            for (idx, variant) in enumerate(variants):
                if int(variant["node"]["price"]) >= min_price:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        if max_price != None:
            for (idx, variant) in enumerate(variants):
                if int(variant["node"]["price"]) <= max_price:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        return variants


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
            """, {"id": variant_id})

        return json.loads(response)["data"]["productVariant"]