'''
Created on 15 de jun de 2016

@author: Thiago Nobrega
@mail: thiagonobrega@gmail.com
'''

import pandas as pd

class NullField():
    """
        Classe utilizada quando o valor  é nulo
    """
    def __init__(self,nome):
        self.nome = nome
        self.sim = 0

def read_result_data(file):
    return pd.read_csv(file,sep=';')  # read the data