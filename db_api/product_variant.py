import json
import shopify
from db_api.config import API_KEY, API_VERSION, APP_PASSWORD, SHOP_URL
from typing import Optional, Text, Union, List, Any
from db_api.schema import Variant, Product
from db_api.product import get_product_by_id


def search_product_variants(
        product_id: Text,
        handle: Text = None,
        color: Optional[Union[Text, List[Text]]] = None,
        size: Optional[Union[Any, List[Any]]] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
):
    if isinstance(color, Text):
        if color:
            color = [color]

    if isinstance(size, List) is False:
        if size:
            size = [size]

    if handle is None:
        handle = get_product_by_id(product_id).handle

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

        if color:
            color = [c.lower() for c in color]
            for (idx, variant) in enumerate(variants):
                if variant["node"]["selectedOptions"][0][
                        "name"] == "Màu sắc" and variant["node"][
                            "selectedOptions"][0]["value"].lower() in color:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        if size:
            size = [s.upper() for s in size if isinstance(s, str)]
            for (idx, variant) in enumerate(variants):
                if variant["node"]["selectedOptions"][1][
                        "name"] == "Kích cỡ" and variant["node"][
                            "selectedOptions"][1]["value"] in size:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        if min_price:
            for (idx, variant) in enumerate(variants):
                if int(variant["node"]["price"]) >= min_price:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        if max_price:
            for (idx, variant) in enumerate(variants):
                if int(variant["node"]["price"]) <= max_price:
                    pass
                else:
                    to_removes.append(idx)
            for to_remove in sorted(to_removes, reverse=True):
                del variants[to_remove]

            to_removes = []

        _variants = []

        for variant in variants:
            _variants.append(Variant.from_dict(product_id=product_id, dict_info=variant, handle=handle))

        return _variants


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
        data = json.loads(response)["data"]["productVariant"]
        product_id = data["product"]["id"]
        handle = data["product"]["handle"]
        variant = Variant.from_dict(product_id=product_id, dict_info=data, handle=handle)
        return variant