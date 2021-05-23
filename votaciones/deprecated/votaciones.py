import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
# from django.template.defaultfilters import slugify
# https://oficial.servel.cl/resultados-definitivos-elecciones-presidencial-parlamentaria-cores-2017/

tempdir = r'G:\Proyectos\elecciones\202101\raw_data'

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_experimental_option("prefs", {
    "download.default_directory": format(tempdir),
    "download.prompt_for_download": False,
})

def click_element(x):
    driver.execute_script("arguments[0].click();", x)

def parse_html_table(soup, header=None):
    rows = []
    for row in soup.find_all('tr'):
        # counter para cada fila
        # si counter = 0, revisar que sea numero. Si no es numero, es nombre de pacto y agregar a todos, caso contrario, es una persona
        newrow = True
        trow = []
        for col in row.find_all('td'):
            texto = col.getText().strip()
            if newrow:
                if texto[0].isdigit():
                    if header is None:
                        trow += [partido, texto] # un postulante
                    else:
                        trow += header + [partido, texto] # un postulante
                    newrow = False
                else:
                    partido = texto # un partdio o coalición
                    newrow = False
                    break
            else:
                trow += [texto]
        if trow:
            rows.append(trow)
    return(rows)

def unfold(listado, counter=0, tag=[]):
    # print(counter, tag)
    driver_ = listado[counter]
    if driver_.tag_name == 'select':
        # flag = tag + [driver_.get_attribute('name')]
        variables = driver_.find_elements_by_tag_name('option')
        for j_, var_ in enumerate(variables):
            # print(j_, len(variables))
            try:
                var_ = driver_.find_elements_by_tag_name('option')[j_]
            except:
                break                
            for i in range(10): # retry 4 times
                try:
                    var_.click()
                    # time.sleep(.1)
                    endtext = var_.text.endswith('...')
                    break
                except StaleElementReferenceException as e:
                    print(e)
                # except Exception as e:
                #     print('retrying 1')
                #     time.sleep(.3*i)
            if not endtext:
                for i in range(10): # retry 4 times
                    try:
                        var_.click()
                        # time.sleep(.1)
                        break
                    except Exception as e:
                        print('retrying 2')
                        time.sleep(.1*i)
                flag = tag + [var_.text]
                if counter >= (len(listado) - 1):
                    print(flag)
                    # body = BeautifulSoup(driver.find_element_by_xpath(tabla).get_attribute('outerHTML'))
                    # ans = parse_html_table(body, flag)
                    # global MAIN 
                    # MAIN += ans
                else: 
                    unfold(listado, counter=counter+1, tag=flag)


url_base = 'https://servelelecciones.cl'  # valores cuota
# eleccion = '//*[@id="menu"]/ul' # constituyentes, gobernadores, alcaldes, etc
eleccion = {'constituyentes': 
                {
                'Generales': '//*[@id="menu"]/ul/li[1]/ul/li[1]/a',
                'Mapuche': '//*[@id="menu"]/ul/li[1]/ul/li[2]/a'
                }
            }
            
detalle = '/html/body/div[2]/div[1]/div[2]/div/form' # region, circ.senatorial
tabla = '//*[@id="basic-table"]/table/tbody[1]'

driver = webdriver.Chrome(options=options)
driver.get(url_base)
time.sleep(3)

click_element(driver.find_element_by_xpath('//*[@id="menu"]/ul/li[1]/ul/li[1]/a'))

elm = driver.find_element_by_xpath(detalle)
lista = [f for f in elm.find_elements_by_tag_name('select') if f.text != '']

MAIN = []
unfold(lista, counter=0, tag=[])



#selRegion




# all = [ {**v, **{'cusip': k}} for k in nuke for v in nuke[k]['cusipAliasRecord'] ]
# pd.DataFrame(all)