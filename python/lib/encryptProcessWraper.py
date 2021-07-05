'''
Created on Fri Mar 17 09:02:21 2017

@author: Thiago Nobrega
@mail: thiagonobrega@gmail.com

'''

import multiprocessing
import csv
from io import StringIO
from util.slicer import Slicer
from lib.datasketch import MinHash
from util import encrypt
import ngram
from lib.mybloom.bloomfilter import BloomFilter


def start_process():
    multiprocessing.current_process()#@UnusedVariable @UndefinedVariable
    #print('Starting ', multiprocessing.current_process().name)#@UnusedVariable @UndefinedVariable

def exec_wrap(data):
    return run(data[0],data[1],data[2],data[3],data[4],data[5])

def run(slicer,slice,first,rowsize,encrypt_flag,bf_size):
    
    mhs = [] 
    
    for i in range(0,rowsize):
        mh = []
        mhs.append(mh)
        
    sdata = StringIO(slicer.read(slice))
    
    reader = csv.reader(sdata,delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
    
    if (first):
        next(reader, None)
    
    
    for row in reader:
        row_size = len(row)
        if(rowsize == row_size):
            for column in range(0,row_size):
                mh = mhs[column]
                local_data = ''
                if encrypt_flag:
                    #TODO: arrumar filtros de bloom
                    bf = encrypt.encryptData(str(row[column]),bf_size)
                    mh.append(bf)

    #return data_stats
    return mhs