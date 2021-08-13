import json
import logging
import pandas as pd
import copy
from selenium import webdriver
from config import DIV_FILTERS, LEVELS
from pathlib import Path

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

DATA = []


def set_logger(name: str, 
                file: Path = None,
                level: int = logging.INFO) -> logging.Logger:  # logging.DEBUG
    """
    Apply logging level and handler to the given logging NAME
    """
    logging_params = {'level': level,
                      'force': True,
                      'format': '%(message)s'}
    if file:
        if file.exists():
            file.unlink()
        logging_params['filename'] = file
        logging_params['filemode'] ='a'
    
    logging.basicConfig(**logging_params)
    logging.info("Starting log")                                
    logger = logging.getLogger(name)
    # logger.setLevel(level)
    return logger


class servelScraper:

    def __init__(self, 
                 logPath: Path = None,
                 mainurl: str = 'servelelecciones.cl'):
        self.logPath: Path = logPath
        self.levels_file: Path = None
        self.levels: pd.DataFrame = None
        # self.logger = self.set_logger('test', logfile)
        self.driver: webdriver = None
        self.mainurl = mainurl
        self.elecciones: pd.DataFrame = None
    
    def set_driver(self, driver):
        self.driver = driver

    def get_elections_list(self):
        url = f'https://{self.mainurl}/modules/menu/config.json'
        data = self.extract_json(self.driver, url)
        self.elecciones = pd.DataFrame([j for f in data for j in f['data'] if f['activo'] is True])

    def get_levels(self, stop_on: str = 'circ_electoral'):
        self.logger = set_logger(self.__class__.__name__, file = self.logPath / 'levels.csv')
        listado = self.unfold(stop_on=stop_on, data_list=[])
        self.levels = listado

    def assembler_url(self,
                      division: str,
                      election: str = 'elecciones_convencionales_g',  # elecciones_gobernadores
                      type: str = 'filtro',
                      value: str = None) -> str:
        """URL assembler

        Parameters:
        division (str): división electoral, debe ser alguno entre 'regiones', 'circ_senatorial', 'distritos', 'comunas', 'circ_electoral', 'locales', 'mesas'.
        election (str): tipo de elección.
        type (str): filtro o computo. El primero para cuando se requiera filtrar y obtener un listado de eleemntos según la división. El segundo para el resultado.
        value (str): código del json a extraer.

        Returns:
        str: La url con el json listo para ser consumido
        """
        url = 'https://{}/data/{}/{}/{}.json'

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
        return url.format(self.mainurl, election, acc, ans)

    @staticmethod
    def parse_info(computo: dict, REG: dict) -> list:
        header = [item for i in REG.values() for item in i.values()] # making a flat list (1D) from the list of lists (2D)
        resumen = [header + ['RESUMEN'] + list(i.values()) for i in computo['resumen']]
        data = [header + [partido['a']] + list(candidato.values()) for partido in computo['data'] for candidato in partido['sd']]
        return data + resumen

    @staticmethod
    def extract_json(driver: webdriver, url: str):
        driver.get(url)
        content = driver.find_element_by_tag_name('pre').text
        return json.loads(content)

    def unfold(self, 
               start: str = 'regiones', 
               val: str = None,
               REG: dict = {},
               stop_on: str = None,
               data_list: list = None):

        global DATA
        url_ = self.assembler_url(start, type='filtro', value=val)
        jsn = self.extract_json(self.driver, url_)
        
        for e in jsn:
            REG[start] = e
            if start != 'mesas':
                clevel = DIV_FILTERS[start]['level'] # nivel actual número
                nlevel = LEVELS[clevel+1] # nivel siguiente palabras
                if stop_on is not None:
                    if stop_on == start:              
                        val_ = [str(item) for i in REG.values() for item in i.values()]
                        DATA.append(val_)
                        logging.info(', '.join(val_))
                        break
                if data_list is None:
                    data_list += self.unfold(nlevel, e['c'], REG, stop_on)
                else:
                    data_list += self.unfold(nlevel, e['c'], REG, stop_on, data_list)
            else:
                print([item for i in REG.values() for item in i.values()])
                data_url = self.assembler_url(start, type='computo', value=e['c'])
                data = self.extract_json(self.driver, data_url)
                votos_mesa = self.parse_info(data, REG)
                if data_list is None:
                    DATA += votos_mesa
                else:
                    return votos_mesa
        
        return data_list