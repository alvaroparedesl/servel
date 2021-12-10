import pandas as pd
import os
import glob
from time import time
from selenium import webdriver
from serlvelscraper import ServelScraper
from concurrent.futures import ThreadPoolExecutor, wait

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

DATA = []


def list_elections(webdriver_path: str,
                   url: str = 'servelelecciones.cl'):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=webdriver_path, options=options)

    ServelScraper(driver, mainurl=url)
    driver.close()


def meta_scraper(webdriver_path: 'str',
                 driver_options: webdriver = None,
                 max_workers: int = 20,
                 headless: bool = True,
                 overwrite_temp: bool = False,
                 **kwargs):
    if headless:
        driver_options.add_argument("--headless")
        print("Running in headless mode")

    start_time = time()
    initd = webdriver.Chrome(executable_path=webdriver_path, options=driver_options)
    initd.implicitly_wait(3)
    inits = ServelScraper(initd, **kwargs)
    # inits.set_driver(initd)

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
                args_ = (row, webdriver_path, driver_options)
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
    result = parse_scraped(all_data, os.path.join(out_dir, 'resultados.xlsx'))

    return True, result


def create_scraper_unit(level,
                        webdriver_path: 'str',
                        driver_options: webdriver = None,
                        **kwargs):
    if driver_options is not None:
        driver = webdriver.Chrome(executable_path=webdriver_path, options=driver_options)
    else:
        driver = webdriver.Chrome(executable_path=webdriver_path)

    driver.implicitly_wait(3)
    scrap = ServelScraper(driver, **kwargs)
    # scrap.set_driver(driver)

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
                'com': 'Comuna', 'votos_n': 'Votos TRICEL', 'local': 'Local',
                'circ': 'Circ.Electoral'}

    ans['cod_reg'] = ans['cod_reg'] % 100
    ans = ans.loc[~ans.opcion.isin(['Válidamente Emitidos', 'Total Votación'])]
    ans.rename(columns=col_dict, inplace=True)
    # ans.to_csv(outfile, encoding='UTF-8', index=False)
    ans.to_excel(outfile, index=False)

    return True

