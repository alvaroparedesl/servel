from servelscraper.auxiliary import participacion
from servelscraper.functions import meta_scraper
from selenium import webdriver
from pathlib import Path
import pandas as pd

# from django.template.defaultfilters import slugify
# https://oficial.servel.cl/resultados-definitivos-elecciones-presidencial-parlamentaria-cores-2017/

tempdir = r'G:\Proyectos\elecciones\202111\raw_data'
chromedriver = r'G:\Proyectos\elecciones\chromedriver.exe'
logPath = Path(r'G:\GIT\servel\servel_scraper\votaciones')

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_experimental_option("prefs", {
    "download.default_directory": format(tempdir),
    "download.prompt_for_download": False,
})

#-- Página principal de los resultados
url_base = 'servelelecciones.cl'

# participacion
# elecciones_presidente

s1, participacion = meta_scraper(webdriver_path=chromedriver,
                                 driver_options=options,
                                 max_workers=20,
                                 headless=True,
                                 overwrite_temp=True,
                                 to_disk=False,
                                 log_path=logPath,
                                 mainurl=url_base,
                                 name='participacion_2021_sv',
                                 election='participacion',
                                 stop_proc='locales',
                                 debug=False,
                                 output_folder='out')

s2, presidenciales = meta_scraper(webdriver_path=chromedriver,
                                  driver_options=options,
                                  max_workers=20,
                                  headless=True,
                                  overwrite_temp=True,
                                  to_disk=False,
                                  log_path=logPath,
                                  mainurl=url_base,
                                  name='presidenciales_2021_sv',
                                  election='elecciones_presidente',
                                  debug=False,
                                  output_folder='out')

presidenciales.loc[:, 'mesas_d'] = presidenciales['mesas_d'].astype(str)
participacion.loc[:, 'Mesa'] = participacion['Mesa'].astype(str)
fin = pd.merge(presidenciales, 
                participacion[['circ_electoral_c', 'locales_c', 'Mesa', 'Total Electores']],
                left_on=['circ_electoral_c', 'locales_c', 'mesas_d'],
                right_on=['circ_electoral_c', 'locales_c', 'Mesa'],
                sort=False,
                how='inner'
               )
fin.shape[0] == presidenciales.shape[0]

fin.to_excel('Resultados_2021_Mesa_PRESIDENCIAL_Tricel_2v_TEMP.xlsx', index=False)
