DIV_FILTERS = {'pais': {'level': 0, 'by': None, 'all': '8056', 'acciones': {'filtro': 'filters', 'computo': 'computo/pais'}},
               'regiones': {'level': 1, 'by': 'byregion', 'all': 'all', 'acciones': {'filtro': 'filters', 'computo': 'computo/regiones'}}, 
               'circ_senatorial': {'level': 2, 'by': 'bycirc_senatorial', 'all': 'all', 'acciones': {'filtro': 'filters', 'computo': 'computo/circ_senatorial'}}, 
               'distritos': {'level': 3, 'by': 'bydistrito', 'all': 'all', 'acciones': {'filtro': 'filters', 'computo': 'computo/distritos'}}, 
               'comunas': {'level': 4, 'by': 'bycomuna', 'all': 'all', 'acciones': {'filtro': 'filters', 'computo': 'computo/comunas'}}, 
               'circ_electoral': {'level': 5, 'by': 'bycirc_electoral', 'all': 'allchile', 'acciones': {'filtro': 'filters', 'computo': 'computo/circ_electoral'}}, 
               'locales': {'level': 6, 'by': 'bylocales', 'all': None, 'acciones': {'filtro': 'filters', 'computo': 'computo/locales'}}, 
               'mesas': {'level': 7, 'by': None, 'all': None, 'acciones': {'filtro': 'filters', 'computo': 'computomesas'} }
               }
LEVELS = {DIV_FILTERS[k]['level']: k for k in DIV_FILTERS}

URLS = {}

'''
$rootScope = angular.element(document).scope()

IGNORAR
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/regiones/all.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/circ_senatorial/all.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/distritos/all.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/comunas/all.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/circ_electoral/allchile.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/distritos/byregion/3015.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/circ_senatorial/byregion/3015.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/mesas/bycirc_electoral/7001.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/locales/bycirc_electoral/7001.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/filters/mesas/bylocales/2176.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/computo/pais/8056.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/computo/regiones/3015.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/computo/distritos/6001.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/computo/comunas/2822.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/computo/circ_electoral/7001.json

https://www.servelelecciones.cl/data/elecciones_convencionales_g/computo/locales/2176.json
https://www.servelelecciones.cl/data/elecciones_convencionales_g/computomesas/70011229.json
'''