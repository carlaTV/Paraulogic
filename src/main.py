import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import unicodedata


def get_config():
    lletres_opcionals = input("Lletres opcionals (separades per comes): ").split(',')
    lletra_obligatoria = input("Lletra obligatòria: ")
    lletres = lletres_opcionals + [lletra_obligatoria]
    return lletres_opcionals, lletra_obligatoria, lletres


def get_combs(lletres, max_group=2):
    print('Generant combinacions...')
    combs = lletres
    if max_group == 1:
        return lletres
    else:
        for i in range(2, max_group + 1):
            combs += [''.join(elem) for elem in itertools.permutations(lletres, i)]
        return combs


def get_all_words(combs):
    solucio = []
    url = 'https://dlc.iec.cat/Results?DecEntradaText={}&AllInfoMorf=False&OperEntrada=1&OperDef=0&OperEx=0&OperSubEntrada=0&OperAreaTematica=0&InfoMorfType=0&OperCatGram=False&AccentSen=False&CurrentPage=0&refineSearch=0&Actualitzacions=False'
    for lletra in combs:
        req = requests.get(url.format(lletra)).text
        req = BeautifulSoup(req, 'html.parser').find_all('a', {'class': 'resultAnchor'})
        for elem in req:
            elem = elem.getText().replace(' ', '')
            solucio.append(elem)
    return set(solucio)


def remove_numbers(input_str):
    return "".join(c for c in input_str if unicodedata.category(c) not in ["No", "Lo"])


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode('utf-8')


def conditions(x, lletra_obligatoria):
    x = remove_accents(x)
    cond1 = len(x) >= 3
    cond2 = lletra_obligatoria in x
    cond3 = set(x) <= set(lletres)
    if cond1 and cond2 and cond3:
        return True
    else:
        return False


if __name__ == '__main__':
    lletres_opcionals, lletra_obligatoria, lletres = get_config()
    combs = get_combs(lletres)

    print(str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min).zfill(2))
    solucio = get_all_words(combs)
    print(str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min).zfill(2))

    df = pd.DataFrame(solucio, columns=['paraules'])
    df['paraules'] = df['paraules'].apply(lambda x: remove_numbers(x))
    df['cond'] = df['paraules'].apply(lambda x: conditions(x, lletra_obligatoria))
    df_res = df[df['cond'] == True]
    df_res.drop_duplicates(subset=['paraules'], inplace=True)
    for val in sorted(df_res[df_res['cond']==True]['paraules'].values):
        print(val)
    print("Hem trobat {} paraules.".format(df_res.shape[0]))
    for elem in df['paraules'].values:
        if set(elem) == set(lletres):
            print('TUTI! '+elem)

