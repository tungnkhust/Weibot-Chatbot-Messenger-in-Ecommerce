from db_api.product import get_products
from db_api.product import get_product_variants


def test_get_product():
    output = get_products(product_type="áo thun", min_price=400000, max_price=800000)
    print(output)