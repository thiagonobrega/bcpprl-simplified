import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib as plt
import time

from lib.mybloom.bloomfilter import BloomFilter
from lib.mybloom.bloomutil import jaccard_coefficient
from encrypt import encrypt_data


def compareBF(encrypted_entities):
    result = []

    for row in encrypted_entities:
        bf1 = row[1]
        bf2 = row[3]

        # splited bf
        a1, b1 = bf1.split()
        a2, b2 = bf2.split()

        real = jaccard_coefficient(bf1, bf2)
        p1 = jaccard_coefficient(a1, a2)
        p2 = jaccard_coefficient(b1, b2)
        hj = (p1 + p2) / 2

        result.append({'id_a': row[0], 'id_b': row[2], 'full': real, 'p1': p1, 'p2': p2, 'hj': hj})

    return pd.DataFrame(result)


def compareBFH(encrypted_entities):
    result = []

    for row in encrypted_entities:
        ida = row[0]
        idb = row[2]

        bf1 = row[1]
        bf2 = row[3]
        result.append(compare_spliting_bf(ida,idb,bf1, bf2, "BBF"))

        try:
            c = bf1.copy()
            xf1 = c.xor_folding()
            c = bf2.copy()
            xf2 = c.xor_folding()
            result.append(compare_spliting_bf(ida, idb, xf1, xf2, "XBF"))
        except ValueError:

            lbs = round(bf1.bit_size / 2)
            cap = round(bf1.capacity / 2)
            print(lbs,cap)
            # import sys
            # sys.exit()
            # print(len(bf1.filter))
            # print(len(bf2.filter))
            result.append({'id_a': ida, 'id_b': idb, 'full': '', 'p1': '', 'p2': '', 'sbf_sim': '', 'bf_type': "XBF"})

        c = bf1.copy()
        bb1 = c.copy().bblip(f=0.01)
        c = bf2.copy()
        bb2 = c.copy().bblip(f=0.01)
        result.append(compare_spliting_bf(ida, idb, bb1, bb2, "BBLIP"))

        c = bf1.copy()
        bb1 = c.copy().blip()
        c = bf2.copy()
        bb2 = c.copy().blip()
        result.append(compare_spliting_bf(ida, idb, bb1, bb2, "BLIP"))

    return pd.DataFrame(result)



def compareMultisplits(encrypted_entities,splits):
    result = []

    for row in encrypted_entities:
        ida = row[0]
        idb = row[2]

        bf1 = row[1]
        bf2 = row[3]
        result.append(compare_multisplit_bf(ida,idb,bf1, bf2, "BBF",n=splits))

# DESCOMENTADO
        try:
            c = bf1.copy()
            xf1 = c.xor_folding()
            c = bf2.copy()
            xf2 = c.xor_folding()
            result.append(compare_multisplit_bf(ida, idb, xf1, xf2, "XBF",n=splits))
        except ValueError:
            lbs = round(bf1.bit_size / 2)
            cap = round(bf1.capacity / 2)
            print(lbs, cap)
        except ZeroDivisionError :
            lbs = round(bf1.bit_size / 2)
            cap = round(bf1.capacity / 2)
            # print()
            print("XBF Zero", lbs,cap)

        # c = bf1.copy()
        # bb1 = c.copy().bblip(f=0.01)
        # c = bf2.copy()
        # bb2 = c.copy().bblip(f=0.01)
        # result.append(compare_multisplit_bf(ida, idb, bb1, bb2, "BBLIP",n=splits))

# descomenytado
        try:
            c = bf1.copy()
            bb1 = c.copy().blip()
            c = bf2.copy()
            bb2 = c.copy().blip()
            result.append(compare_multisplit_bf(ida, idb, bb1, bb2, "BLIP",n=splits))
        except ZeroDivisionError :
            lbs = round(bf1.bit_size / 2)
            cap = round(bf1.capacity / 2)
            print(lbs,cap)
            print("BLIP Zero")

    return pd.DataFrame(result)

def compare_multisplit_bf(ida,idb,bf1, bf2, tipo,n=1):

    real = jaccard_coefficient(bf1, bf2)



    out = {'id_a': ida, 'id_b': idb, 'full': real, 'bf_type': tipo ,
           'orignal_bits_size': bf1.bit_size , 'splits' : 2**n}

    bf1_parts = split_bf(bf1,n)
    bf2_parts = split_bf(bf2, n)

    z = []
    d = []
    m = int(2**n)
    for i in range(0,m):
        z.append(jaccard_coefficient(bf1_parts[i],bf2_parts[i]))
        d.append(abs(real-jaccard_coefficient(bf1_parts[i], bf2_parts[i])))

    median, mean , std , min , max = np.median(z), np.mean(z), np.std(z) , np.min(z) , np.max(z)

    out['psim_median'] = median
    out['psim_mean'] = mean
    out['psim_min'] = min
    out['psim_max'] = max
    out['sbf_sim'] = np.sum(z)/len(z)
    out['part_bit_size'] = bf1_parts[0].bit_size


    out['median_dist_of_real'] = np.median(d)
    out['mean_dist_of_real'] = np.mean(d)
    out['max_dist_of_real'] = np.min(d)
    out['min_dist_of_real'] = np.max(d)
    out['std_dist_of_real'] = np.std(d)


    return out


    #return {'id_a': ida, 'id_b': idb, 'full': real, 'p1': p1, 'p2': p2, 'sbf_sim': hj, 'bf_type': tipo}

def split_bf(bf,n):
    if n > 1:
        a,b = bf.split()
        return split_bf(a,n-1) + split_bf(b,n-1)
    return bf.split()

def compare_spliting_bf(ida,idb,bf1, bf2, tipo):

    a1, b1 = bf1.split()
    a2, b2 = bf2.split()
    real = jaccard_coefficient(bf1, bf2)
    p1 = jaccard_coefficient(a1, a2)
    p2 = jaccard_coefficient(b1, b2)
    hj = (p1 + p2) / 2.0
    return {'id_a': ida, 'id_b': idb, 'full': real, 'p1': p1, 'p2': p2, 'sbf_sim': hj, 'bf_type': tipo}


def parallel_compare(datadir, basename, e1_fields, e2_fields, bflen, fp = 0.01, ngrams=2, lpower=256, enc='utf-8', set_p=None):

    ed = encrypt_data(datadir, basename, e1_fields, e2_fields, bflen, set_p=set_p)
    df = compareBFH(ed)
    df['p'] = str(int(set_p * 100)) + "%"
    b = BloomFilter(cap=bflen)
    b.set_hashfunction_by_p(set_p)
    df['hash_funcions'] = b.hash_functions
    return df

def parallel_compare_multisplit(ed, splits):

    # ed = encrypt_data(datadir, basename, e1_fields, e2_fields, bflen, set_p=0.5)
    df = compareMultisplits(ed,splits=splits)
    # b = BloomFilter(cap=bflen) colocar fora
    return df

def plotResult(domain,fname,att1,att2,size=96,encoding='utf-8'):
    #ebikes = encrypt_data('bikes', 'candset.csv', [3,4,7] , [8,9,12], 96, lpower=256)
    ed = encrypt_data(domain, fname, att1, att2, size, lpower=256 ,enc=encoding)
    df = compareBF(ed)

    df['diff'] = abs(df.full - df.hj) * 100
    #ax = df.boxplot('diff',title="Bikes")
    #fig = ax[0][0].get_figure()
    ax = df.boxplot('diff')
    fig = ax.get_figure()
    plt.title("Diferenca da similaridade p/ a base " + domain)
    plt.xlabel("")
    plt.ylabel("Diferença em %")
    fig.show()
    fig.savefig(domain+'.png')


########
######## Analises dos resultados

def isTrueMatch(gs,ida,idb,base_a='idDBLP',base_b='idACM'):
    """
     Utilizando dict para ser mais rapido

    :param gs:
    :param ida:
    :param idb:
    :param base_a:
    :param base_b:
    :return:
    """
    try:
        if ( gs[str(ida)+str(idb)] == True ):
            return True
    except KeyError:
        return False

def isTrueMatchOriginal(gs,ida,idb,base_a='idDBLP',base_b='idACM'):
    try:
        z = gs[(gs[base_a] == ida) & (gs[base_b] == idb)]
    except KeyError:
        return False
    if len(z) == 1:
        return True

    return False

def simulated_sbf_protocol(df,goldstandard,threshold_a,error=0.02,original_bf_len=1024):
    """
    Simula a abordagem ABEL

    :param df: UM DATAFRAME COM A SIMILARIDADE
    :param goldstandard: o gabarito
    :param threshold_a: o limiar alfa
    :param error: O erro para calcular o limiar beta
    :param original_bf_len: Tamanho original do filtro de Bloom
    :return:
    """

    s = len(df)
    t = threshold_a-error
    result = []
    count = 0

    for index, row in df.iterrows():
        save_flag = True
        rp = {'id_a': row['id_a'], 'id_b': row['id_b'] ,
              'split_sim': row['split_sim'], 'sbf_sim': row['sbf_sim'], 'bf_sim': row['full_bf'],
              'original_bflen': original_bf_len , 'sbf_splits': row['splits'],
              'alfa': threshold_a , 'beta_error' : error}

        if row['split_sim'] >= t:
            rp['abel_1st_s'] = True
        else:
            rp['abel_1st_s'] = False

        if row['sbf_sim'] >= threshold_a:
            if isTrueMatch(goldstandard, row['id_a'], row['id_b']):
                rp['sbf_stat'] = 'TM'
            else:
                rp['sbf_stat'] = 'FM'
        else:
            if isTrueMatch(goldstandard, row['id_a'], row['id_b']):
                rp['sbf_stat'] = 'FTM' # Fault TM
                save_flag = False
            else:
                save_flag = False
            #     rp['sbf_stat'] = 'TFM' # TFM


        if row['full_bf'] >= threshold_a:
            if isTrueMatch(goldstandard, row['id_a'], row['id_b']):
                rp['bf_stat'] = 'TM' #criar metodo
            else:
                rp['bf_stat'] = 'FM'  # criar metodo
        else:
            if isTrueMatch(goldstandard, row['id_a'], row['id_b']):
                save_flag = False
                rp['bf_stat'] = 'FTM' # Fault TM
            else:
                save_flag = False
            #     rp['bf_stat'] = 'TFM' # TFM

        if save_flag:
            result.append(rp)

        count += 1
        if count % 500000 == 0:
            print(count / s * 100)

    return pd.DataFrame(result)