from db_api.order import create_order
from db_api.product import search_products, get_product_by_id
from db_api.product_variant import get_product_variant_by_id, search_product_variants
from db_api.collection import get_collections


def test_get_products():
    response = search_products(product_type=None, color="xanh than")
    print(response)
    print(len(response))


if __name__ == "__main__":
    print(
        create_order(
            items=[
                {
                    "variantId": "gid://shopify/ProductVariant/42093440598230",
                    "quantity": 2,
                }
            ],
        )
    )
    # print(get_collections())
    # test_get_products()
    # print('-' * 50)
    # print(get_product_by_id("gid://shopify/Product/7461429575894"))
    # print(search_product_variants(product_id="gid://shopify/Product/7461449793750", color="trắng"))
    # print(get_product_variant_by_id("gid://shopify/ProductVariant/42101616509142"))
