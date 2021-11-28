from functions import meta_scraper
from selenium import webdriver
from pathlib import Path

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
                       max_workers=20,
                       headless=True,
                       overwrite_temp=False,
                       log_path=logPath,
                       mainurl=url_base,
                       name='presidenciales_2021_pv',
                       election='elecciones_presidente',
                       debug=False,
                       output_folder='out')

