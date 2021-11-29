import json
import yaml


def write_yaml(data, file_path, **kwargs):
    if "encoding" in kwargs:
        encoding = kwargs['encoding']
    else:
        encoding = 'utf-8'
    with open(file_path, 'w', encoding=encoding) as pf:
        yaml.dump(data, pf, allow_unicode=True, default_flow_style=False, sort_keys=False)


def load_yaml(file_path, **kwargs):
    if "encoding" in kwargs:
        encoding = kwargs['encoding']
    else:
        encoding = 'utf-8'
    with open(file_path, 'r', encoding=encoding) as pf:
        return yaml.load(pf)


def write_json(data, file_path, **kwargs):
    if "encoding" in kwargs:
        encoding = kwargs['encoding']
    else:
        encoding = 'utf-8'
    with open(file_path, 'w', encoding=encoding) as pf:
        json.dump(data, pf, ensure_ascii=False, indent=4)


def load_json(file_path, **kwargs):
    if "encoding" in kwargs:
        encoding = kwargs['encoding']
    else:
        encoding = 'utf-8'
    with open(file_path, 'r', encoding=encoding) as pf:
        return json.load(pf)