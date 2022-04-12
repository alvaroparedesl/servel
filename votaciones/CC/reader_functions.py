import lxml
import pandas as pd
from urllib import request
from lxml import objectify


def flatten_dict(obj: lxml.objectify, keys: dict = {}):  #, items: list = []):
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

    items = []
    if children:
        for c in children:
            # # TODO: revisar, por recursividad entrega una lista a veces [ni idea como arreglarlo]
            # y = flatten_dict(c, keys)
            # if isinstance(y, dict):  # este if es la solución al problema anterior
            #     items.append(y)
            y = flatten_dict(c, keys)
            if isinstance(y, list):
                items.extend(y)
            else:
                items.append(y)
    else:
        return keys

    return items


def read_parse(url: str, id: str, to_pandas: bool = True):
    content = request.urlopen(url)
    sc = content.read()
    pp = objectify.fromstring(sc)
    if to_pandas:
        temp = flatten_dict(pp)
        if len(temp) > 0:
            df = pd.DataFrame(temp)
            df['id'] = id
            return df
        else:
            return None
    else:
        return flatten_dict(pp)
