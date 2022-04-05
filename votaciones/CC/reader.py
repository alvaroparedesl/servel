import pandas as pd
from urllib import request
from reader_functions import read_parse

listaComisiones = 'https://www.cconstituyente.cl/WSConvencionConstitucional/WSConvencionConstitucional.asmx/getListaComisiones'
listaConvencionales = 'https://www.cconstituyente.cl/WSConvencionConstitucional/WSConvencionConstitucional.asmx/getListaConvencionales'
listaSesionesPleno = 'https://www.cconstituyente.cl/WSConvencionConstitucional/WSConvencionConstitucional.asmx/getListaSesionesPleno'

urlVotacionComisiones = 'https://www.cconstituyente.cl/WSConvencionConstitucional/WSConvencionConstitucional.asmx/getVotacionesXComision?prmComisionID={}'
urlAsistenciaComisiones = 'https://www.cconstituyente.cl/WSConvencionConstitucional/WSConvencionConstitucional.asmx/getAsistenciaXComision?prmComisionID={}'

comisiones = pd.read_xml(request.urlopen(listaComisiones))
convencionales = pd.read_xml(request.urlopen(listaConvencionales))
convencionales = pd.read_xml(request.urlopen(listaSesionesPleno))

comisionesVot = [];
comisionesAsis = [];

for i, v in comisiones.iterrows():
    id = v.ComisionID
    print(f'Comision {id}: {v.Nombre}')
    comisionesVot.append(read_parse(urlVotacionComisiones.format(id)))
    comisionesAsis.append(read_parse(urlAsistenciaComisiones.format(id)))

votacionsComision = pd.concat(comisionesVot)
asistenciaComision = pd.concat(comisionesAsis)


## Export
comisiones.to_csv('data/comisiones.csv', index=False)
votacionsComision.to_csv('data/votacionComisiones.csv', index=False)
asistenciaComision.to_csv('data/asistenciaComisiones.csv', index=False)
