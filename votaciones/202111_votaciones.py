from functions import ServelScraper, meta_scraper
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

scraped = meta_scraper(chromedriver_path=chromedriver,
                       driver_options=options,
                       max_workers=60,
                       headless=True,
                       log_path=logPath,
                       mainurl=url_base,
                       name='presidenciales_2021_pv',
                       election='elecciones_presidente',
                       debug=False,
                       output_folder='out')

## ----------- OLD
driver = webdriver.Chrome(executable_path=chromedriver, options=options)
driver.implicitly_wait(3)

scrap = ServelScraper(log_path=logPath,
                      mainurl=url_base,
                      name='presidenciales_2021_pv',
                      election='elecciones_presidente',
                      debug=False)
scrap.set_driver(driver)
scrap.get_elections_list()

# Para optimizar, es necesario obtener un listado de las circunscripciones antes de repartir el trabajo
# Usualmente es cirunscripción electoral, que el nivel superior antes de que se deba hacer una elección en el siguiente nivel
# y abrir los resultados: se puede ver en config.DIV_FILTERS
scrap.get_levels('circ_electoral', overwrite=False)



scrap = ServelScraper(log_path=logPath,
                      mainurl=url_base,
                      name='presidenciales_2021_pv',
                      election='elecciones_presidente',
                      debug=False,
                      output_folder='out')
scrap.set_driver(driver)
scrap.get_levels('circ_electoral', overwrite=False)

sl = scrap.levels.iloc[0]

# ans = scrap.unfold(start='locales',
#                    val=sl.cod_circ,
#                    REG={'regiones': {'c': sl.cod_reg, 'd': sl.reg},
#                         'circ_senatorial': {'c': sl.cod_cs, 'd': sl.cs},
#                         'distritos': {'c': sl.cod_dis, 'd': sl.dis},
#                         'comunas': {'c': sl.cod_com, 'd': sl.com},
#                         'circ_electoral': {'c': sl.cod_circ, 'd': sl.circ}
#                         },
#                    stop_on=None,
#                    data_list=[])


ans = scrap.export_unfold(start='locales',
                   val=sl.cod_circ,
                   REG={'regiones': {'c': sl.cod_reg, 'd': sl.reg},
                        'circ_senatorial': {'c': sl.cod_cs, 'd': sl.cs},
                        'distritos': {'c': sl.cod_dis, 'd': sl.dis},
                        'comunas': {'c': sl.cod_com, 'd': sl.com},
                        'circ_electoral': {'c': sl.cod_circ, 'd': sl['Circ.Electoral']}
                        },
                   stop_on=None,
                   data_list=[])