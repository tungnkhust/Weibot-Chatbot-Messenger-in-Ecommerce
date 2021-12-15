from db_api.schema import Product


def test_get_level_product(object_type="áo len"):
    level = Product.get_level_of_object_type(object_type)
    print(object_type, level)


if __name__ == '__main__':
    test_get_level_product()
