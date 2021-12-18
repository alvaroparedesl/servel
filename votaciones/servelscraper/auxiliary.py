import pandas as pd


def selector(what: str):
    switcher = {
        'participacion': participacion,
        'elecciones_presidente': elecciones_presidente
    }
    return switcher.get(what, None)


def elecciones_presidente(df: pd.DataFrame):
    ans = df.loc[~df['Nombre de los Candidatos'].isin(['Válidamente Emitidos', 'Total Votación'])]
    ans.loc[:, 'tipo_mesa'] = ans['mesas_d'].str.extract(r'(V|M)$').fillna('')
    return ans


def participacion(df: pd.DataFrame):
    ans = df.loc[~df['Mesa'].isin(['TOTAL'])]
    ans.loc[:, 'tipo_mesa'] = ans['Mesa'].str.extract(r'(V|M)$').fillna('')
    return ans
