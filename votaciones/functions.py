import json
from selenium import webdriver
from config import DIV_FILTERS, LEVELS
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

DATA = []

def ensamble_url(division: str,
                 election: str = 'elecciones_convencionales_g',
                 type: str = 'filtro',
                 value: str = None) -> str:
    """URL ensambler

    Parameters:
    division (str): división electoral, debe ser alguno entre 'regiones', 'circ_senatorial', 'distritos', 'comunas', 'circ_electoral', 'locales', 'mesas'.
    election (str): tipo de elección.
    type (str): filtro o computo. El primero para cuando se requiera filtrar y obtener un listado de eleemntos según la división. El segundo para el resultado.
    value (str): código del json a extraer.

    Returns:
    str: La url con el json listo para ser consumido
    """
    url = 'https://www.servelelecciones.cl/data/{}/{}/{}.json'

    div = DIV_FILTERS[division]
    acc = div['acciones'][type]

    ans_ = []
    if type == 'filtro':
        ans_.append(division)
        nivel = div['level']
        if nivel > 1: # mayor a regiones, podría ser desde regiones si hay un filtro por país para elecciones en el extranjero.
            parent = LEVELS[nivel - 1]
            ans_.append(DIV_FILTERS[parent]['by'])
        else:
            pass
    elif acc == 'computo':
        # TODO: testear con otros valores que no sea 'computomesas'
        pass

    if value is None:
        val_ = div['all']
        if val_ is None:
            raise Exception("Value is None and there's no default value for this division: {}".format(division))
        else:
            ans_.append(val_)
    else:
        ans_.append(str(value))

    ans = '/'.join(ans_)
    return url.format(election, acc, ans)


def parse_info(computo: dict, REG: dict) -> list:
    header = [item for i in REG.values() for item in i.values()] # making a flat list (1D) from the list of lists (2D)
    resumen = [header + ['RESUMEN'] + list(i.values()) for i in computo['resumen']]
    data = [header + [partido['a']] + list(candidato.values()) for partido in computo['data'] for candidato in partido['sd']]
    return data + resumen
    

def extract_json(driver: webdriver, url: str):
    driver.get(url)
    content = driver.find_element_by_tag_name('pre').text
    return json.loads(content)


def unfold(driver: webdriver,
           start: str = 'regiones', 
           val: str = None,
           REG: dict = {}):

    url_ = ensamble_url(start, type='filtro', value=val)
    jsn = extract_json(driver, url_)
    
    for e in jsn:
        REG[start] = e
        if start != 'mesas':
            clevel = DIV_FILTERS[start]['level'] # nivel actual número
            nlevel = LEVELS[clevel+1] # nivel siguiente palabras
            unfold(driver, nlevel, e['c'], REG)
        else:
            print([item for i in REG.values() for item in i.values()])
            data_url = ensamble_url(start, type='computo', value=e['c'])
            data = extract_json(driver, data_url)
            votos_mesa = parse_info(data, REG)
            global DATA  # podría haber usado una variable de entrada, pero la idea es no perder lo avanzado
            DATA += votos_mesa