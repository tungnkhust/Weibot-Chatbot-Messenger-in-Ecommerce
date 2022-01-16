from rasa_sdk import Action, Tracker
from actions.utils.mapper.entity_mapper import string_simulate
from typing import List
import re

from db_api.schema import Product


def check_in_list(element, elements, lower_case=True):
    if isinstance(element, str) is False:
        element = str(element)

    elements = [str(e) for e in elements]

    if lower_case:
        elements = [e.lower() for e in elements]
        if element.lower() in elements:
            return True

    if element in elements:
        return True

    return False


def get_product_by_object_type(object_type, products: List[Product]):
    candidate_scores = {}
    for product in products:
        score = string_simulate(object_type, product.title, lower=True)
        candidate_scores[product] = score

    candidate_ranking = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    product, best_score = candidate_ranking[0]
    return product, best_score


def get_generic_message(elements):
    message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": elements
            }
        }
    }
    return message


def get_order_confirmation(variants):
    message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "receipt",
                "order_number": "12345678902",
                "currency": "NVĐ",
                "order_url": "http://petersapparel.parseapp.com/order?order_id=123456",
                "timestamp": "1428444852",
                "address": {
                    "street_1": "1 Hacker Way",
                    "street_2": "",
                    "city": "Menlo Park",
                    "postal_code": "94025",
                    "state": "CA",
                    "country": "US"
                },
                "summary": {
                    "subtotal": 75.00,
                    "shipping_cost": 4.95,
                    "total_tax": 6.19,
                    "total_cost": 56.14
                },
                "adjustments": [
                    {
                        "name": "New Customer Discount",
                        "amount": 20
                    },
                    {
                        "name": "$10 Off Coupon",
                        "amount": 10
                    }
                ],
                "elements": [
                    {
                        "title": "Classic White T-Shirt",
                        "subtitle": "100% Soft and Luxurious Cotton",
                        "quantity": 1,
                        "price": 50,
                        "currency": "USD",
                        "image_url": "http://petersapparel.parseapp.com/img/whiteshirt.png"
                    },
                    {
                        "title": "Classic Gray T-Shirt",
                        "subtitle": "100% Soft and Luxurious Cotton",
                        "quantity": 1,
                        "price": 25,
                        "currency": "USD",
                        "image_url": "http://petersapparel.parseapp.com/img/grayshirt.png"
                    }
                ]
            }
        }
    }
