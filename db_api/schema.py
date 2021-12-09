import os
import re
from typing import Any, Text, List, Union, Dict
from db_api.config import SHOP_URL


class Variant:
    def __init__(
            self,
            id: Text = None,
            product_id: Text = None,
            handle: Text = None,
            display_name: Text = None,
            inventory_quantity: int = 0,
            price: float = None,
            color: Text = None,
            size: Text = None,
            images: List[Text] = None
    ):
        self.id = id
        self.product_id = product_id
        self.handle = handle
        self.display_name = display_name
        self.inventory_quantity = inventory_quantity
        self.price = int(price)
        self.color = color
        self.size = size
        self.images = images if images else []
        self.variant_id = re.search("[\d]+", self.id).group()
        self.url = self._get_url()

    def _get_url(self):
        if self.handle:
            url = SHOP_URL + f"/products/{self.handle}?variant={self.variant_id}"
        else:
            url = None
        return url

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.id,
            "handle": self.handle,
            "display_name": self.display_name,
            "inventory_quantity": self.inventory_quantity,
            "price": self.price,
            "color": self.color,
            "size": self.size,
            "images": self.images,
            "url": self.url
        }

    @classmethod
    def from_dict(cls, product_id, dict_info: Dict, handle: Text = None):
        if "node" in dict_info:
            variant_info = dict_info["node"]
        else:
            variant_info = dict_info
        id = variant_info["id"]
        display_name = variant_info["displayName"]
        inventory_quantity = variant_info["inventoryQuantity"]
        price = float(variant_info["price"])
        color = None
        size = None

        for option in variant_info["selectedOptions"]:
            if option["name"] == "Màu sắc":
                color = option["value"]
            elif option["name"] == "Kích cỡ":
                size = option["value"]
        if variant_info["image"]:
            images = [variant_info["image"]["src"]]
        else:
            images = []

        return cls(
            id=id,
            product_id=product_id,
            handle=handle,
            display_name=display_name,
            inventory_quantity=inventory_quantity,
            price=price,
            color=color,
            size=size,
            images=images
        )

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

    def to_messenger_element(self):
        element = {
            "title": self.display_name,
            "image_url": self.images[0],
            "buttons": [
                {
                    "type": "web_url",
                    "url": self.url,
                    "title": "Xem chi tiết",
                }
            ]
        }
        return element

    def to_messenger_image(self):
        elements = []
        for img in set(self.images):
            elements.append({
                "title": self.color,
                "image_url": img
            })
        return elements


class Product:
    def __init__(
            self,
            id: Text = None,
            handle: Text = None,
            title: Text = None,
            tags: List[Text] = None,
            total_inventory: int = 0,
            product_type: Text = None,
            description: Text = None,
            min_price: float = None,
            max_price: float = None,
            variants: List[Variant] = None,
            colors: List[Text] = None,
            sizes: List[Union[Text, int]] = None,
            images: List[Text] = None,

    ):
        self.id = id
        self.handle = handle
        self.title = title
        self.tags = tags if tags else []
        self.total_inventory = total_inventory
        self.product_type = product_type
        self.description = description
        self.min_price = int(min_price)
        self.max_price = int(max_price)
        self.variants = variants if variants else []
        self.colors = colors if colors else []
        self.sizes = sizes if sizes else []
        self.images = images if images else []
        self.url = SHOP_URL + f"/products/{self.handle}"
        self.gender = self._get_gender()

    def _get_gender(self):
        for tag in self.tags:
            if tag in ["nam", "nữ"]:
                return tag
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "handle": self.handle,
            "title": self.title,
            "tags": self.tags,
            "total_inventory": self.total_inventory,
            "product_type": self.product_type,
            "description": self.description,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "colors": self.colors,
            "sizes": self.sizes,
            "images": self.images,
            "url": self.url
        }

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash(self.id)

    def to_info_element(self):
        element = {
            "title": self.title,
            "image_url": self.images[0],
            "subtitle": f"{int(self.min_price)}VND-{int(self.max_price)}VND\n",
            "default_action": {
              "type": "web_url",
              "url": self.url,
              "messenger_extensions": False,
              "webview_height_ratio": "tall"
            },
            "buttons": [
              {
                "type": "web_url",
                "url": self.url,
                "title": "Xem chi tiết"
              }
            ]
          }
        return element

    def to_messenger_element(self):
        element = {
            "title": self.title,
            "image_url": self.images[0],
            "buttons": [
                {
                    "type": "web_url",
                    "url": self.url,
                    "title": "Xem chi tiết",
                }
            ]
        }
        return element

    @classmethod
    def from_dict(cls, dict_info: Dict):
        if "node" in dict_info:
            product_info = dict_info["node"]
        else:
            product_info = dict_info

        id = product_info["id"]
        handle = product_info["handle"]
        title = product_info["title"]
        tags = product_info["tags"]
        total_inventory = product_info["totalInventory"]
        product_type = product_info["productType"]
        description = product_info["description"]
        min_price = float(product_info["priceRangeV2"]["minVariantPrice"]["amount"])
        max_price = float(product_info["priceRangeV2"]["maxVariantPrice"]["amount"])
        options = product_info["options"]
        colors = []
        sizes = []
        for option in options:
            if option["name"] == "Màu sắc":
                colors = option["values"]
            elif option["name"] == "Kích cỡ":
                sizes = option["values"]
        images = []
        for img in product_info["images"]["edges"]:
            images.append(img["node"]["src"])

        return cls(
            id=id,
            handle=handle,
            title=title,
            tags=tags,
            total_inventory=total_inventory,
            product_type=product_type,
            description=description,
            min_price=min_price,
            max_price=max_price,
            colors=colors,
            sizes=sizes,
            images=images
        )

