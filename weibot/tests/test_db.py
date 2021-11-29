from db_api import get_product_variants, get_products


def test_get_products(sex=None, product_type=None, min_price=None, max_price=None):
    response = get_products(sex=sex, product_type=product_type, min_price=min_price, max_price=max_price)
    print(response)
    print(len(response))


if __name__ == '__main__':
    test_get_products()
    print('-'*50)
    test_get_products(product_type="áo thun")
    test_get_products(product_type="áo len")
