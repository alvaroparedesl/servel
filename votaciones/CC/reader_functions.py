import lxml
import pandas as pd
from urllib import request
from lxml import objectify


def flatten_dict(obj: lxml.objectify, keys: dict = {}, items: list = []):
    """
    Make a nested xml object into a flat list of dicts

    @param obj:
    @param keys:
    @param items:
    @return:
    """
    attrs = {k: v.pyval for k, v in vars(obj).items() if hasattr(v, 'pyval')}
    if attrs:
        keys = dict(keys, **attrs)

    children = [v for v in obj.getchildren() if not hasattr(v, 'pyval')]

    if children:
        for c in children:
            y = flatten_dict(c,
                             keys)  # TODO: revisar, por recursividad entrega una lista a veces [ni idea como arreglarlo]
            if isinstance(y, dict):  # este if es la solución al problema anterior
                items.append(y)
    else:
        return keys

    return items


def read_parse(url: str, to_pandas: bool = True):
    content = request.urlopen(url)
    sc = content.read()
    pp = objectify.fromstring(sc)
    if to_pandas:
        return pd.DataFrame(flatten_dict(pp))
    else:
        return flatten_dict(pp)