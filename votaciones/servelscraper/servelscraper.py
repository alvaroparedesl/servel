import json
import logging
import pandas as pd
import os
from selenium import webdriver
from servelscraper.config import DIV_FILTERS, LEVELS
from pathlib import Path

DATA = []


class ServelScraper:

    def __init__(self,
                 driver: webdriver,
                 log_path: Path = None,
                 mainurl: str = 'servelelecciones.cl',
                 name: str = 'elecciones',
                 election: str = None,
                 debug: bool = False,
                 output_folder: str = '',
                 **kwargs):  # extra args not used here
        self.kwargs = kwargs
        self.logPath: Path = log_path
        self.levels_file: Path = None
        self.levels: pd.DataFrame = None
        self.levels_columns = ['cod_reg', 'reg', 'cod_cs', 'cs', 'cod_dis', 'dis', 'cod_com', 'com', 'cod_circ', 'circ']
        # self.logger = self.set_logger('test', logfile)
        self.driver: webdriver = driver
        self.mainurl = mainurl
        self.elecciones: pd.DataFrame = None
        self.name: str = name
        self.election: str = election
        self.debug = debug
        self.outputFolder = Path(output_folder)
        self.outputFolder.mkdir(parents=True, exist_ok=True)
        self.columns = ["opcion", "partido", "votos_n", "votos_per", "candidato", "es_electo", "sd"]
        if election is None:
            self.get_elections_list(summary=True)

    def set_driver(self, driver):
        self.driver = driver

    def get_elections_list(self, overwrite: bool = False, summary: bool = False):
        if self.elecciones is None or overwrite:
            url = f'https://{self.mainurl}/modules/menu/config.json'
            data = self.extract_json(self.driver, url)
            self.elecciones = pd.DataFrame([j for f in data for j in f['data'] if f['activo'] is True])
        if summary:
            print(self.elecciones.iloc[:, range(4)])

    def get_levels(self, stop_on: str = 'circ_electoral', overwrite: bool = True):
        self.levels_file = self.logPath / f'{self.name}_levels.csv'
        read_url = True
        if os.path.isfile(self.levels_file):
            if not overwrite:
                read_url = False
            self.levels = self.parse_levels(self.levels_file, levels_columns=self.levels_columns)
        if read_url:
            # self.logger = set_logger(self.__class__.__name__, file=self.levels_file)
            listado = self.unfold(stop_on=stop_on, data_list=[])  # vacío
            self.levels = self.parse_levels(object=listado, levels_columns=self.levels_columns)
            self.levels.to_csv(self.levels_file, index=False, encoding='UTF-8')

    @staticmethod
    def parse_levels(file: str = None, object: list = None, levels_columns: list = []):
        if file is None:
            df = pd.DataFrame(object)
            df.columns = levels_columns
        else:
            df = pd.read_csv(file, encoding='UTF-8')
        return df

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

        if self.debug:
            print('DEBUG: Variable division', division)
        div = DIV_FILTERS[division]
        acc = div['acciones'][type]

        ans_ = []
        if type == 'filtro':
            ans_.append(division)
            nivel = div['level']
            if nivel > 1:  # mayor a regiones, podría ser desde regiones si hay un filtro por país para elecciones en el extranjero.
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
        header = [f'{i}_{v}' for i in REG for v in REG[i]] + list(computo['title'].values())
        leftdata = [item for i in REG.values() for item in
                    i.values()]  # making a flat list (1D) from the list of lists (2D)
        resumen = [leftdata + list(i.values()) for i in computo['resumen']]
        # data = [header + [partido['a']] + list(candidato.values()) for partido in computo['data'] for candidato in partido['sd']]
        data = [leftdata + list(partido.values()) for partido in computo['data']]
        return header, data + resumen  # armar directamente pd.DataFrame podría ser más lento, pero más cómodo

    @staticmethod
    def extract_json(driver: webdriver, url: str):
        driver.get(url)
        content = driver.find_element_by_tag_name('pre').text
        return json.loads(content)

    def export_unfold(self, **kwargs):
        temp_ = self.unfold(**kwargs)
        body = [k for i in temp_ for k in i[1:]]
        header = list(set(tuple(v[0]) for v in temp_))[0]
        ans = pd.DataFrame(body, columns=header)
        sl = kwargs['REG']
        # out_name = f'{sl.cod_com}-{sl.com}-{sl.cod_circ}-{sl.cod_circ}.csv'
        OUT_NAME = '{0}-{1}-{2}-{3}-{4}-{5}.csv'

        out_name = OUT_NAME.format(sl["regiones"]["c"], sl["regiones"]["d"],
                                   sl["comunas"]["c"], sl["comunas"]["d"],
                                   sl["circ_electoral"]["c"], sl["circ_electoral"]["d"])
        #
        # ans.columns = self.levels_columns + ['cod_local', 'local', 'cod_mesa', 'mesas_fusionadas', 'n1',
        #                                      'n2'] + self.columns # + ['n3']

        ans.to_csv(self.outputFolder / out_name, index=False, encoding='UTF-8')

        return True

    def unfold(self,
               start: str = 'regiones',
               val: str = None,
               REG: dict = {},
               stop_on: str = None,  # stop before, but without processing
               stop_proc: str = None,  # stop before and proceess like mesas
               data_list: list = None):

        global DATA
        if self.debug:
            print('DEBUG: Variable start', start)
        url_ = self.assembler_url(start, election=self.election, type='filtro', value=val)
        jsn = self.extract_json(self.driver, url_)

        for e in jsn:
            REG[start] = e
            if start not in ('mesas', stop_proc):
                clevel = DIV_FILTERS[start]['level']  # nivel actual número
                nlevel = LEVELS[clevel + 1]  # nivel siguiente palabras
                if stop_on is not None:
                    if stop_on == start:
                        val_ = [str(item) for i in REG.values() for item in i.values()]
                        DATA.append(val_)
                        # logging.info(', '.join(val_))
                        continue
                if data_list is None:
                    data_list = self.unfold(nlevel, e['c'], REG, stop_on, stop_proc)
                else:
                    data_list = self.unfold(nlevel, e['c'], REG, stop_on, stop_proc, data_list)
            else:
            # if start == 'mesas' or start == stop_proc:
                # print([item for i in REG.values() for item in i.values()])
                data_url = self.assembler_url(start, election=self.election, type='computo', value=e['c'])
                data = self.extract_json(self.driver, data_url)
                header, body = self.parse_info(data, REG)
                if data_list is None:
                    data_list = [[header] + body]
                else:
                    data_list += [[header] + body]

        if stop_on is None:
            return data_list
        else:
            return DATA

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
            logging_params['filemode'] = 'a'

        logging.basicConfig(**logging_params)
        logging.info("Starting log")
        logger = logging.getLogger(name)
        # logger.setLevel(level)
        return logger