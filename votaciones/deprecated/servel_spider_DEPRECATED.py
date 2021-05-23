import json
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.template.defaultfilters import slugify

firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = True
driver = webdriver.Firefox(capabilities=firefox_capabilities)


def fetch_url(ul, minimal=True):
    urlinfo = None
    counter = 1
    readed = False
    while urlinfo is None:  # try until you can read correctly the data
        try:
            driver.get(ul)
            d1 = driver.find_element_by_tag_name('body').text
            readed = True
        except Exception:
            print 'Failed page lecture. Attempt {}'.format(counter)
            time.sleep(1)
            if counter > 20:
                driver.quit()
            else:
                counter += 1

        if readed:
            try:
                urlinfo = json.loads(d1.encode('utf8'))   # cp1252
            except Exception:
                if minimal:
                    try:
                        urlinfo = json.loads(d1)
                    except Exception:
                        global driver
                        driver.quit()
                        driver = webdriver.Firefox(capabilities=firefox_capabilities)

                    if urlinfo:
                        for pos in xrange(len(urlinfo)):
                            try:
                                urlinfo[pos][u'd'] = urlinfo[pos][u'd'].encode('utf8')
                            except:
                                urlinfo[pos][u'd'] = slugify(urlinfo[pos][u'd'])
                else:
                    global driver
                    driver.quit()
                    driver = webdriver.Firefox(capabilities=firefox_capabilities)

    return urlinfo


def parse_info(dat, aux):
    aux1 = dat['colegioEscrutador']
    extra = dat['resumen']
    #             CODIGO_MESA, NOMBRE_MESA,  C,   CODIGO_COLEGIO_ESCRUTADOR, D, DV, NEV, NR, R 
    auxe = aux + [aux1['cm'], aux1['nm'], aux1['c'], aux1['cc'], aux1['d'], aux1['dv'], aux1['nev'], aux1['nr'], aux1['r']]
    ans = []
    for v in dat['data']:
        for s in v['sd']:
            if s['sd'] is None:
                # aux, PACTO, SUBPACTO, PARTIDO, NOMBRE, VOTOS, ELECTO
                ans.append(auxe + [v['a'], None, s['b'], s['a'], s['c'], s['f']!=''])
            else:
                for d in s['sd']:
                    ans.append(auxe + [v['a'], s['a'], d['b'], d['a'], d['c'], d['f']!=''])
    
    ans.append(auxe + [None]*3 + ["Votos Nulos", extra[1]['c'], None])
    ans.append(auxe + [None]*3 + ["Votos en Blancos", extra[2]['c'], None])
    # return [[v['a'], s['a'], s['b'], s['c'], s['f']!=''] for v in dat['data'] for s in val['sd']]
    return ans

def parse_info_presidente(dat, aux):
    aux1 = dat['colegioEscrutador']
    extra = dat['resumen']
    #             CODIGO_MESA, NOMBRE_MESA,  C,   CODIGO_COLEGIO_ESCRUTADOR, D, DV, NEV, NR, R 
    auxe = aux + [aux1['cm'], aux1['nm'], aux1['c'], aux1['cc'], aux1['d'], aux1['dv'], aux1['nev'], aux1['nr'], aux1['r']]
    ans = []
    for v in dat['data']:
        ans.append(auxe + [v['a'], v['b'], v['c'], v['f']!=''])  # a: Nombre; b:ni idea (en blanco??); c:votos, f:ganador=*
    
    ans.append(auxe + ["Votos Nulos", None, extra[1]['c'], None])
    ans.append(auxe + ["Votos en Blancos", None, extra[2]['c'], None])
    # return [[v['a'], s['a'], s['b'], s['c'], s['f']!=''] for v in dat['data'] for s in val['sd']]
    return ans
    

# url = 'http://www.servelelecciones.cl/data/'    # segunda vuelta
url = 'http://pv.servelelecciones.cl/data/'  # primera vuelta
# tipo = ['alcalde', 'consejal', 'participacion']
tipo = ['elecciones_presidente']
data = []
counter = 0

for tp in tipo:
    # tp = tipo[0]
    comunas = fetch_url('{}{}/filters/comunas/all.json'.format(url, tp))
    for comuna in comunas:
        # comuna = comunas[0]
        circuns = fetch_url('{}{}/filters/circ_electoral/bycomuna/{}.json'.format(url, tp, comuna['c']))
        for circun in circuns:
            # circun = circuns[0]
            locales = fetch_url('{}{}/filters/locales/bycirc_electoral/{}.json'.format(url, tp, circun['c']))
            for local in locales:
                # local = locales[0]
                mesas = fetch_url('{}{}/filters/mesas/bylocales/{}.json'.format(url, tp, local['c']))
                for mesa in mesas:
                    # mesa = mesas[0]
                    print 'Count {}|--- Comuna: {}, Ciruncscripcion: {}, Local: {}, Mesa: {}'\
                        .format(counter, comuna['c'], circun['c'], local['c'], mesa['c'])
                    # info = fetch_url('{}{}/computo/mesas/{}.json'.format(url, tp, mesa['c']), minimal=False)
                    info = fetch_url('{}{}/computomesas/{}.json'.format(url, tp, mesa['c']), minimal=False)
                    # TIPO ELECCION, COD_COM, NOM_COM, COD_CIRC, NOM_CIRC, LOCAL_COD, LOCAL_NOM
                    au = [tp, comuna['c'], comuna['d'], circun['c'], circun['d'], local['c'], local['d']]
                    mesar = parse_info_presidente(info, au)
                    data.extend(mesar)
                    counter += 1

# final1; data2
# data = [f for f in data if f[2] != u"HUARA"]
final = pd.DataFrame(data)
nombres = ["TIPO ELECCION", "COD_COM", "NOM_COM", "COD_CIRC", "NOM_CIRC", "COD_LOCAL", "NOM_LOCAL",
           "COD_MESA", "NOM_MESA", "C", "COD_COLEGIO_ESCRUTADOR", "D", "DV", "NEV", "NR", "R", 
           "CANDIDATO", "Blanco", "VOTOS", "ELECTO"]
           #"PACTO", "SUBPACTO", "PARTIDO", "NOMBRE", "VOTOS", "ELECTO"]
final.columns = nombres
final.to_excel("F:/2017_primera_vuelta.xlsx")
                    
                    
                    
if False:           
    pass
    # alcalde, concejal, participacion
    # http://www.servelelecciones.cl/data/alcalde/filters/regiones/all.json # listado de regiones
    # http://www.servelelecciones.cl/data/alcalde/filters/circ_senatorial/all.json #
    # http://www.servelelecciones.cl/data/alcalde/filters/distritos/all.json #
    # http://www.servelelecciones.cl/data/alcalde/filters/comunas/all.json #
    # http://www.servelelecciones.cl/data/alcalde/filters/circ_electoral/all.json #

    # http://www.servelelecciones.cl/data/alcalde/computo/pais/8001.json
    # http://www.servelelecciones.cl/data/alcalde/computo/regiones/3013.json
    # http://www.servelelecciones.cl/data/alcalde/computo/comunas/114501.json   # aisen
    # http://www.servelelecciones.cl/data/alcalde/filters/circ_electoral/bycomuna/114501.json # aisen
    # http://www.servelelecciones.cl/data/alcalde/computo/circ_electoral/7491.json # aisen / aisen
    # http://www.servelelecciones.cl/data/alcalde/filters/locales/bycirc_electoral/7491.json # aisen / aisen
    # http://www.servelelecciones.cl/data/alcalde/filters/mesas/bycirc_electoral/7491.json # aisen / aisen
    # http://www.servelelecciones.cl/data/alcalde/computo/locales/1238.json # aisen / aisen / local
    # http://www.servelelecciones.cl/data/alcalde/computo/mesas/4910001.json # aisen / aisen / mesas
    '''
    Primero, listar comunas e Iterar sobre ellas:
    http://www.servelelecciones.cl/data/alcalde/filters/comunas/all.json

        Filtrar circunscripcion por comuna
        http://www.servelelecciones.cl/data/alcalde/filters/circ_electoral/bycomuna/{comuna}.json

            Filtrar local de votacion por circunscripcion
            http://www.servelelecciones.cl/data/alcalde/filters/locales/bycirc_electoral/{circ}.json

                Filtrar mesa por local de votacion
                http://www.servelelecciones.cl/data/alcalde/filters/mesas/bylocales/{local}.json

                    Por cada mesa, extraer datos
                    http://www.servelelecciones.cl/data/alcalde/computo/mesas/{mesa}.json
    '''
   
# import scrapy
# from scrapy import signals
# # from scrapy.shell import inspect_response
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy.http import TextResponse

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# # https://blog.scrapinghub.com/2016/04/20/scrapy-tips-from-the-pros-april-2016-edition/
# # https://blog.scrapinghub.com/2015/03/02/handling-javascript-in-scrapy-with-splash/
# # https://blog.scrapinghub.com/2016/05/18/scrapy-tips-from-the-pros-may-2016-edition/
# # http://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path


# class ServelSpider(scrapy.Spider):
    # name = 'servels'
    # start_urls = ['http://www.servelelecciones.cl/']
    # download_delay = 2

    # def __init__(self, filename=None):
        # # wire us up to selenium
        # self.driver = webdriver.Firefox()
        # dispatcher.connect(self.spider_closed, signals.spider_closed)

    # def spider_closed(self, spider):
        # self.driver.close()

    # def parse(self, response):
        # item = {}
        # # Load the current page into Selenium
        # self.driver.get(response.url)
        # try:
            # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'selRegion')))
        # except TimeoutException:
            # item['status'] = 'timed out'

        # # Sync scrapy and selenium so they agree on the page we're looking at then let scrapy take over
        # resp = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
        # # scrape as normal
        # for region in resp.css('select#selRegion > option ::attr(value)').extract():
        # # resp.css('select#selRegion > ::attr()').extract()
            # print region
            # yield scrapy.FormRequest(
                # 'http://www.servelelecciones.cl/',
                # formdata={'region': region},
                # callback=self.parse_comuna
            # )

    # def parse_comuna(self, response):
        # item = {}
        # # Load the current page into Selenium
        # self.driver.get(response.url)
        # try:
            # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'selComunas')))
        # except TimeoutException:
            # item['status'] = 'timed out'

        # # Sync scrapy and selenium so they agree on the page we're looking at then let scrapy take over
        # resp = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

        # import pdb; pdb.set_trace()
        # for comuna in resp.css('div#selComunas > option ::attr(value)').extract():
        # # resp.css('div#selCircunscripcionElectorales').extract():
            # with open('F:/test.html', 'wb') as f: f.write(resp.body)
            # yield scrapy.FormRequest.from_response(
                # response,
                # formdata={'comunas': comuna},
                # callback=self.parse_results,
            # )

    # def parse_results(self, response):
        # import pdb; pdb.set_trace()
