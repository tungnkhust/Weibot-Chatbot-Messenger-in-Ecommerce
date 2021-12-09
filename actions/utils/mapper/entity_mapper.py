import os
import re
import json
import jellyfish
import warnings
from abc import ABC, abstractmethod
from typing import Dict, List, Union
from collections import Counter, defaultdict


def no_accent_vietnamese(s):
    s = re.sub('[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub('[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub('[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub('[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub('[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub('[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub('[ìíịỉĩ]', 'i', s)
    s = re.sub('[ÌÍỊỈĨ]', 'I', s)
    s = re.sub('[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub('[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub('[ỳýỵỷỹ]', 'y', s)
    s = re.sub('[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub('Đ', 'D', s)
    s = re.sub('đ', 'd', s)
    return s


def levenshtein_score(s1: str, s2: str):
    return 1 - jellyfish.levenshtein_distance(s1, s2)/max(len(s1), len(s2))


def string_simulate(s1: str, s2: str, no_accent_ratio=0.3, lower=True):
    if lower:
        s1 = s1.lower()
        s2 = s2.lower()
    raw_score = levenshtein_score(s1, s2)
    no_accent_score = levenshtein_score(no_accent_vietnamese(s1), no_accent_vietnamese(s2))
    score = (1 - no_accent_ratio) * raw_score + no_accent_ratio * no_accent_score
    return score


class EntityMapper:
    """
    Entity Mapper to mapping value detect by nlp model to root value.
    Example: chieens luoc, chiến lược, si -> si
    Test:
        mapper = EntityMapper()
        mapper.load('/home/tungnk/Desktop/working/LTA_project/fvrie-nlu/ontology/ontology.json')
        value = mapper.map(entity='department', value='ai center')
        print(value)
    """

    def __init__(self, ontology: Dict = None, threshold=0.8, entity_value=None, **kwargs):
        self.ontology = ontology
        self.threshold = threshold
        self.entity_value = entity_value

    def map(self, entity, value, **kwargs):
        if entity not in self.ontology:
            score = 1
            return value, score
        candidates = self.ontology[entity]
        candidate_scores = {
            candidate: string_simulate(value.lower(), candidate.lower()) for candidate in candidates
        }
        candidate_ranking = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        best_syn_val, best_score = candidate_ranking[0]
        if best_score >= self.threshold:
            root_value = self.ontology[entity][best_syn_val]
            score = best_score
        else:
            root_value = value
            score = 1

        return root_value, score

    def load(self, ontology_path='./data/synonym_entity_mapper.json', **kwargs):
        # TODO: Initialize ontology
        ontology = dict()

        # TODO: Check exists ontology_path
        # If True, Load ontology, else return empty ontology and warning.
        if ontology_path.endswith('.json'):
            with open(ontology_path, 'r') as pf:
                entity_value = json.load(pf)

            entity_value = entity_value.get('synonyms', {})
            for entity in entity_value:
                ontology[entity] = {}
                for root_value in entity_value[entity]:
                    entities = entity_value[entity][root_value]
                    for value in entities:
                        ontology[entity][value] = root_value
        else:
            print(
                f"[Warning] `ontology_path`:{ontology_path} not exists or wrong format. \n"
                f"Extension format must be .json. \n"
                f"Return `ontology=dict()`. \n"
            )

        self.ontology = ontology