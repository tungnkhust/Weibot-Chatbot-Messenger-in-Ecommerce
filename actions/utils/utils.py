from rasa_sdk import Action, Tracker
from actions.utils.mapper.entity_mapper import string_simulate
from typing import List
import re

from db_api.schema import Product


def get_product_by_object_type(object_type, products: List[Product]):
    candidate_scores = {}
    for product in products:
        score = string_simulate(object_type, product.title, lower=True)
        candidate_scores[product] = score

    candidate_ranking = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    product, best_score = candidate_ranking[0]
    return product, best_score

