'''
Created on 9 de abr de 2017

@author: Thiago
'''


import csv
import os
import time
import datetime

import pandas as pd
from bitarray import bitarray
import ngram
# from web3 import Web3, HTTPProvider

# from lib.util.bc import *
from lib.mybloom.bloomfilter import BloomFilter
from lib.mybloom.bloomutil import *
# from deploy import compileContract
from lib.util.env import getbase_dir

def encryptData(data,size,fp=0.01,n=2,bpower=8,p=None):
    """
        n : 2 = Bigrams
        size : Size of BF
        fp : False positive rate
    """
    bloomfilter = BloomFilter(size,fp,bfpower=bpower)
    if p != None:
        bloomfilter.set_hashfunction_by_p(p)

    index = ngram.NGram(N=n)
    bigrams = list(index.ngrams(index.pad(str(data))))

    for bigram in bigrams:
        bloomfilter.add(str(bigram))

    return bloomfilter

# '0xC1844bbe0537cE51F95F9EC08c55D697fCcf3f17'
def bitarray2int(ba):
    import struct
    return int(ba.to01(), 2)

def int2bitarray(num):
    return bitarray.bitarray(num)

def convertBF2BC_slow(bf):
    one = bytes(True)
    zero = bytes(False)
    bffilter = []

    for i in bf.filter:
        if( bytes(i) == one):
            bffilter.append(1)
        else:
            bffilter.append(0)

    # bytes(bffilter)
    return bytes(bffilter)
def convertBF2BC(bf):
    return bytes(bf.filter)
# end encrypt

import pkgutil
import encodings
import os

def all_encodings():
    modnames = set([modname for importer, modname, ispkg in pkgutil.walk_packages(
        path=[os.path.dirname(encodings.__file__)], prefix='')])
    aliases = set(encodings.aliases.aliases.values())
    return modnames.union(aliases)

def encrypt_data(datadir, basename, e1_fields, e2_fields, bflen, fp = 0.01, ngrams=2, lpower=256, enc='utf-8', set_p=None):

    base_dir = getbase_dir(['Datasets',datadir]) # + os.sep

    rows = []
    # print(base_dir+basename)
    with open(base_dir + basename, encoding=enc, errors='replace') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                try:
                    dbf1 = row[e1_fields[0]]
                    for i in e1_fields[1:]:
                        dbf1 = dbf1 + row[i]

                    dbf2 = row[e2_fields[0]]
                    for i in e2_fields[1:]:
                        dbf2 = dbf2 + row[i]

                    #dbf1 = row[3] + row[4] + row[7]
                    #dbf2 = row[8] + row[9] + row[12]

                    if set_p == None:
                        erow = [row[1], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower), row[2], encryptData(dbf2, bflen, fp=fp, n=ngrams,bpower=lpower)]
                    else:
                        erow = [row[1], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower, p=set_p), row[2],
                                encryptData(dbf2, bflen, fp=fp, n=ngrams, bpower=lpower, p=set_p)]
                    rows.append(erow)
                    line_count += 1
                except IndexError:
                    print(row)
                    print(e1_fields)
                    print(e2_fields)
            # print(f'Processed {line_count} lines.')
    return rows

def encrypt_data2(datadir, basename, e1_fields, bflen, fp = 0.01, ngrams=2, lpower=256, enc='utf-8', set_p=None):

    base_dir = getbase_dir(['Datasets',datadir]) # + os.sep

    rows = []
    # print(base_dir+basename)
    with open(base_dir + basename, encoding=enc, errors='replace') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                try:
                    dbf1 = row[e1_fields[0]]
                    for i in e1_fields[1:]:
                        dbf1 = dbf1 + row[i]

                    if set_p == None:
                        erow = [row[0], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower)]
                    else:
                        erow = [row[0], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower, p=set_p)]
                    rows.append(erow)
                    line_count += 1
                except IndexError:
                    print(row)
                    print(e1_fields)
            # print(f'Processed {line_count} lines.')
    return rows

def encrypt_data_in_memory(df, e1_fields, bflen, fp = 0.01, ngrams=2, lpower=256, enc='utf-8', set_p=None):

    rows = []
    line_count = 0

    for index, row in df.iterrows():
        if line_count == 0:
            line_count += 1
        else:
            try:
                dbf1 = str(row[e1_fields[1]])
                for i in e1_fields[1:]:
                    dbf1 = dbf1 + str(row[i])

                # print(dbf1)
                if set_p == None:
                    erow = [row[0], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower)]
                else:
                    erow = [row[0], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower, p=set_p)]
                rows.append(erow)
                line_count += 1
            except IndexError:
                print(row)
                print(e1_fields)
        # print(f'Processed {line_count} lines.')
    return rows

def parallel_encrypt_data(outpdatadir, basename, e1_fields, e2_fields, bflen, fp = 0.01, ngrams=2, lpower=8, enc='utf-8', set_p=None):

    base_dir = getbase_dir('Datasets') + datadir + os.sep

    rows = []
    # print(base_dir+basename)
    with open(base_dir + basename, encoding=enc, errors='replace') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                try:
                    dbf1 = row[e1_fields[0]]
                    for i in e1_fields[1:]:
                        dbf1 = dbf1 + row[i]

                    dbf2 = row[e2_fields[0]]
                    for i in e2_fields[1:]:
                        dbf2 = dbf2 + row[i]

                    #dbf1 = row[3] + row[4] + row[7]
                    #dbf2 = row[8] + row[9] + row[12]

                    if set_p == None:
                        erow = [row[1], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower), row[2], encryptData(dbf2, bflen, fp=fp, n=ngrams,bpower=lpower)]
                    else:
                        erow = [row[1], encryptData(dbf1, bflen, n=ngrams, fp=fp, bpower=lpower, p=set_p), row[2],
                                encryptData(dbf2, bflen, fp=fp, n=ngrams, bpower=lpower, p=set_p)]
                    rows.append(erow)
                    line_count += 1
                except IndexError:
                    print(row)
                    print(e1_fields)
                    print(e2_fields)
            # print(f'Processed {line_count} lines.')
    return rows

def exec_comparasion_regular_vs_bcjaccard(rows,web3,dc,sleep_time=0.5):
    results = [['id_l','id_r','regular_jaccard','exec_time_regular','bc_jaccard','calc_bcjaccard','exec_time_bc','estimated_gas']]

    row_count = 0
    for row in rows:
        # print(row_count)
        row_count += 1
        print(row_count,len(rows))
        bcbf1= convertBF2BC(row[1])
        bcbf2= convertBF2BC(row[3])

        try:
            estimated_gas = dc.functions.compareEntities(bcbf1, bcbf2).estimateGas()
            # print("\t Well estimated")
        except ValueError:
            estimated_gas = 100000
            # print("\t Not Well estimated")

        transaction = {'from': account, 'gas': estimated_gas +1, 'to': dc.address}

        start_bc = time.time()
        try:
            i,u , j = dc.functions.compareEntities(bcbf1, bcbf2).call()
            bcjac = j
            calc_bcjac = i/u
        except Exception as e:
            print(e)
            bcjac = -1
            calc_bcjac = -1
        end_bc = time.time()

        start_rj = time.time()
        regularjac = jaccard_coefficient(row[1],row[3])
        end_rj = time.time()

        id_l = row[0]
        id_r = row[2]
        r = [id_l,id_r,regularjac,end_rj-start_rj,bcjac,calc_bcjac,end_bc-start_bc,estimated_gas]
        results.append(r)
        time.sleep(sleep_time)
    return results

# import pandas as pd
# r = exec_comparasion_regular_vs_bcjaccard(encrypted_entities[0:5],web3,deployed_contract,bitlen=128,sleep_time=0.7)
# df = pd.DataFrame.from_records(r[1:], columns=r[0])
# print(df[['regular_jaccard' , 'bc_jaccard']])
# del r , df



# reogranizar em outro local
def get_DeployedContract(web3, contract_name, contract_address, contract_srcfile):
    # cdir = getbase_dir('Contracts')
    cc = compileContract(contract_srcfile)
    abi = cc['contracts'][contract_srcfile][contract_name]['abi']

    dc = web3.eth.contract(
        address=contract_address,
        abi=abi,
    )
    return dc

def save2csv(data,epath,file_name,bpath='..'+os.sep+'results'+os.sep):
    os.makedirs(bpath+epath, exist_ok=True)
    headers = data[0]
    df = pd.DataFrame.from_records(data[1:], columns=headers)
    df.to_csv(bpath+epath+os.sep+file_name, sep=';', encoding='utf-8')


def convertBloomFilter2Ints(bf, word_size,endian='big'):
    # 'little'
    ints = []
    bff = bf.filter;

    niter = bff.length() / word_size
    # if not isinstance(niter,int):
    if bff.length() % word_size != 0:
        raise Exception('The bloomfilter length/wordsize should be a interger, however it was: {}'.format(niter))
    niter = int(niter)

    start = 0
    for i in range(1, niter + 1):
        end = word_size * i
        val = int.from_bytes(bff[start:end].tobytes(), byteorder=endian, signed=False)
        ints.append(val)
        start = end

    return ints


def fromIntes2bits(ints, word_size,endian='big'):
    output = bitarray(endian=endian)

    for i in ints:
        p = bitarray(endian=endian)
        z = i.to_bytes(int(word_size / 8), endian)
        p.frombytes(z)
        output.extend(p)

    return output

def saveBF2JSON(bf_list,bfpart_sep="#",bf_sep="!",bflen=256):
    index = 1
    out = str(index) + ";"

    first_bf = True
    for bf in bf_list:
        first = True

        if first_bf:
            first_bf = False
        else:
            out = out + bf_sep

        for bfpart in convertBloomFilter2Ints(bf, 256):
            if first:
                out = out + str(bfpart)
                first = False
            else:
                out = out + bfpart_sep +str(bfpart)

    return out