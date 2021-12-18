from votaciones.servelscraper.functions import servelScraper
from selenium import webdriver
from pathlib import Path

# from django.template.defaultfilters import slugify
# https://oficial.servel.cl/resultados-definitivos-elecciones-presidencial-parlamentaria-cores-2017/

tempdir = r'G:\Proyectos\elecciones\202101\raw_data'
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
url_base = 'pv.servelelecciones.cl'

driver = webdriver.Chrome(executable_path=chromedriver, options=options)
driver.implicitly_wait(3)

scrap = servelScraper(logPath=logPath, mainurl=url_base)
scrap.set_driver(driver)
scrap.get_elections_list()

# Para optimizar, es necesario obtener un listado de las circunscripciones antes de repartir el trabajo
# Usualmente es cirunscripción electoral, que el nivel superior antes de que se deba hacer una elección en el siguiente nivel
# y abrir los resultados: se puede ver en config.DIV_FILTERS
scrap.get_levels('circ_electoral')  # correr sólo una vez

scrap.get_election()

scrap.driver.get(url_base)

ans = scrap.unfold(driver)