import os
import re


def get_url(product_info):
    shop_url = "https://" + os.getenv("SHOP_URL")
    # variant_id = re.search("[\d]+", product_info["id"]).group()
    url = shop_url + f"/products/{product_info['handle']}"
    return url


def get_shop_url():
    shop_url = "https://" + os.getenv("SHOP_URL")
    return shop_url
