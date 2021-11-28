import json
import logging
import pandas as pd
import os
import glob
from time import time
from selenium import webdriver
from config import DIV_FILTERS, LEVELS
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

DATA = []


def meta_scraper(chromedriver_path: 'str',
                 driver_options: webdriver = None,
                 max_workers: int = 20,
                 headless: bool = True,
                 overwrite_temp: bool = False,
                 **kwargs):
    if headless:
        driver_options.add_argument("--headless")
        print("Running in headless mode")

    start_time = time()
    initd = webdriver.Chrome(executable_path=chromedriver_path, options=driver_options)
    initd.implicitly_wait(3)
    inits = ServelScraper(**kwargs)
    inits.set_driver(initd)

    print('Getting levels....')
    inits.get_levels('circ_electoral', overwrite=False)
    print('Levels retrieved....')
    initd.close()

    futures = []
    out_dir = os.path.join(kwargs['output_folder'], kwargs['name'])
    temp_dir = os.path.join(out_dir, "temp")
    kwargs['output_folder'] = temp_dir
    print('Starting pooling')
    print(f'Temporary folder: {temp_dir}')
    print(f'Output folder: {out_dir}')

    OUT_NAME = '{0}-{1}-{2}-{3}-{4}-{5}.csv'

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, row in inits.levels.iterrows():
            go = True
            if not overwrite_temp:
                out_name = OUT_NAME.format(row['cod_reg'], row['reg'], row['cod_com'],
                                           row['com'], row['cod_circ'], row['circ'])
                if os.path.isfile(os.path.join(temp_dir, out_name)):
                    go = False
            if go:
                args_ = (row, chromedriver_path, driver_options)
                futures.append(
                    executor.submit(create_scraper_unit, *args_, **kwargs)
                )

    wait(futures)
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")

    print('Starting parsing')
    all_files = glob.glob(os.path.join(temp_dir, "*.csv"))
    all_data = pd.concat((pd.read_csv(f) for f in all_files))
    parse_scraped(all_data, os.path.join(out_dir, 'resultados.xlsx'))

    return True


def create_scraper_unit(level,
                        chromedriver_path: 'str',
                        driver_options: webdriver = None,
                        **kwargs):
    if driver_options is not None:
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=driver_options)
    else:
        driver = webdriver.Chrome(executable_path=chromedriver_path)

    driver.implicitly_wait(3)
    scrap = ServelScraper(**kwargs)
    scrap.set_driver(driver)

    reg_dict = {'regiones': {'c': level.cod_reg, 'd': level.reg},
                'circ_senatorial': {'c': level.cod_cs, 'd': level.cs},
                'distritos': {'c': level.cod_dis, 'd': level.dis},
                'comunas': {'c': level.cod_com, 'd': level.com},
                'circ_electoral': {'c': level.cod_circ, 'd': level.circ}
                }
    ans = scrap.export_unfold(start='locales',
                              val=level.cod_circ,
                              REG=reg_dict,
                              stop_on=None,
                              data_list=[])

    driver.close()

    return True, ans


def parse_scraped(df: pd.DataFrame, outfile: str):
    ans = df.drop(columns=['sd', 'votos_per', 'es_electo', 'n1', 'n2'])

    ans['Mesa'] = ans['mesas_fusionadas'].str.split('-').str[0]
    ans['Tipo mesa'] = ans['Mesa'].str.extract(r'(V|M)$').fillna('')

    col_dict = {'cod_reg': 'Nro.Región', 'reg': 'Región', 'mesas_fusionadas': 'Mesas Fusionadas',
                'com': 'Comuna', 'votos_n': 'Votos TRICEL', 'local': 'Local'}

    ans['cod_reg'] = ans['cod_reg'] % 100
    ans = ans.loc[~ans.opcion.isin(['Válidamente Emitidos', 'Total Votación'])]
    ans.rename(columns=col_dict, inplace=True)
    # ans.to_csv(outfile, encoding='UTF-8', index=False)
    ans.to_excel(outfile, index=False)


class ServelScraper:

    def __init__(self,
                 log_path: Path = None,
                 mainurl: str = 'servelelecciones.cl',
                 name: str = 'elecciones',
                 election: str = 'elecciones_presidente',
                 debug: bool = False,
                 output_folder: str = ''):
        self.logPath: Path = log_path
        self.levels_file: Path = None
        self.levels: pd.DataFrame = None
        self.levels_columns = ['cod_reg', 'reg', 'cod_cs', 'cs', 'cod_dis', 'dis', 'cod_com', 'com', 'cod_circ', 'circ']
        # self.logger = self.set_logger('test', logfile)
        self.driver: webdriver = None
        self.mainurl = mainurl
        self.elecciones: pd.DataFrame = None
        self.name: str = name
        self.election: str = election
        self.debug = debug
        self.outputFolder = Path(output_folder)
        self.outputFolder.mkdir(parents=True, exist_ok=True)
        self.columns = ["opcion", "partido", "votos_n", "votos_per", "candidato", "es_electo", "sd"]

    def set_driver(self, driver):
        self.driver = driver

    def get_elections_list(self):
        url = f'https://{self.mainurl}/modules/menu/config.json'
        data = self.extract_json(self.driver, url)
        self.elecciones = pd.DataFrame([j for f in data for j in f['data'] if f['activo'] is True])

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
        header = [item for i in REG.values() for item in
                  i.values()]  # making a flat list (1D) from the list of lists (2D)
        resumen = [header + list(i.values()) for i in computo['resumen']]
        # data = [header + [partido['a']] + list(candidato.values()) for partido in computo['data'] for candidato in partido['sd']]
        data = [header + list(partido.values()) for partido in computo['data']]
        return data + resumen

    @staticmethod
    def extract_json(driver: webdriver, url: str):
        driver.get(url)
        content = driver.find_element_by_tag_name('pre').text
        return json.loads(content)

    def export_unfold(self, **kwargs):
        temp_ = self.unfold(**kwargs)
        ans = pd.DataFrame(temp_)
        sl = kwargs['REG']
        # out_name = f'{sl.cod_com}-{sl.com}-{sl.cod_circ}-{sl.cod_circ}.csv'
        OUT_NAME = '{0}-{1}-{2}-{3}-{4}-{5}.csv'

        out_name = OUT_NAME.format(sl["regiones"]["c"], sl["regiones"]["d"],
                                   sl["comunas"]["c"], sl["comunas"]["d"],
                                   sl["circ_electoral"]["c"], sl["circ_electoral"]["d"])

        ans.columns = self.levels_columns + ['cod_local', 'local', 'cod_mesa', 'mesas_fusionadas', 'n1',
                                             'n2'] + self.columns # + ['n3']

        ans.to_csv(self.outputFolder / out_name, index=False, encoding='UTF-8')

        return True

    def unfold(self,
               start: str = 'regiones',
               val: str = None,
               REG: dict = {},
               stop_on: str = None,
               data_list: list = None):

        global DATA
        if self.debug:
            print('DEBUG: Variable start', start)
        url_ = self.assembler_url(start, election=self.election, type='filtro', value=val)
        jsn = self.extract_json(self.driver, url_)

        for e in jsn:
            REG[start] = e
            if start != 'mesas':
                clevel = DIV_FILTERS[start]['level']  # nivel actual número
                nlevel = LEVELS[clevel + 1]  # nivel siguiente palabras
                if stop_on is not None:
                    if stop_on == start:
                        val_ = [str(item) for i in REG.values() for item in i.values()]
                        DATA.append(val_)
                        # logging.info(', '.join(val_))
                        continue
                if data_list is None:
                    data_list = self.unfold(nlevel, e['c'], REG, stop_on)
                else:
                    data_list = self.unfold(nlevel, e['c'], REG, stop_on, data_list)
            else:
                # print([item for i in REG.values() for item in i.values()])
                data_url = self.assembler_url(start, election=self.election, type='computo', value=e['c'])
                data = self.extract_json(self.driver, data_url)
                votos_mesa = self.parse_info(data, REG)
                if data_list is None:
                    data_list = votos_mesa
                else:
                    data_list += votos_mesa

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
