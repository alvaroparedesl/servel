import sys
from functions import unfold, DATA
from selenium import webdriver

sys.path.append(r'G:\GIT\servel')
# from django.template.defaultfilters import slugify
# https://oficial.servel.cl/resultados-definitivos-elecciones-presidencial-parlamentaria-cores-2017/

tempdir = r'G:\Proyectos\elecciones\202101\raw_data'
chromedriver = r'G:\Proyectos\elecciones\chromedriver.exe'

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_experimental_option("prefs", {
    "download.default_directory": format(tempdir),
    "download.prompt_for_download": False,
})

url_base = 'https://servelelecciones.cl'  # valores cuota
# eleccion = '//*[@id="menu"]/ul' # constituyentes, gobernadores, alcaldes, etc
eleccion = {'constituyentes': 
                {
                'Generales': '//*[@id="menu"]/ul/li[1]/ul/li[1]/a',
                'Mapuche': '//*[@id="menu"]/ul/li[1]/ul/li[2]/a'
                }
            }

# Usando selectores            
division = {'Región': '#selRegion',
            'Circunscripción Senatorial': '#selCircunscripcionSenatorial',
            'Distrito': '#selDistrito',
            'Comunas': '#selComunas',
            'Circunscripción Electoral': '#selCircunscripcionElectorales',
            'Locales de Votación': '#selLocalesVotacion',
            'Mesas Receptoras': '#selMesasReceptoras'}
 

driver = webdriver.Chrome(executable_path=chromedriver, options=options)
driver.implicitly_wait(3)
driver.get(url_base)
unfold(driver)
