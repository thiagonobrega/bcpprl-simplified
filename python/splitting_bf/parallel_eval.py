import numpy as np
from splitting_bf.evaluation import *
import multiprocessing as mp
from lib.util.env import getbase_dir


def process(datadir, basename, e1_fields, e2_fields, bflen):
    pool = mp.Pool(processes=8)
    results = [pool.apply_async(parallel_compare, args=(datadir, basename, e1_fields , e2_fields, bflen), kwds={'set_p': p})
               for p in np.arange(0.1,1.0,0.1)]
    output = [p.get() for p in results]


    df = output[0]
    for pdf in output[1:]:
        df = df.append(pdf,ignore_index = True)

    df['diff'] = abs(df.full - df.sbf_sim) * 100

    # ax = df.boxplot('diff',by='p',rot=30)
    ax = df.boxplot('diff', by=['p', 'bf_type'], rot=90, figsize=(18, 10))
    fig = ax.get_figure()
    plt.title("")
    plt.xlabel("")
    plt.ylabel("Diferença em %")
    fig.savefig(getbase_dir('results')+datadir+'.png')
    df.to_csv(getbase_dir('results')+datadir+'.csv',sep=';')
    print('Done ' + datadir + "!")



process('bikes', 'candset.csv', [3,4,7] , [8,9,12],96)
process('beer', 'sample-candset.csv', [1,3,4] , [2,5,6],96)
process('books1', 'candset.csv', [1,3,4,5] , [2,6,7,8],256)
process('eletronics', 'sample-candset.csv', [1,4,5,3] , [2,6,7,8],1024)
process('movies1', 'candset.csv', [1,3,4,5] , [2,6,7,8],768)
process('music', 'sample-candset.csv', [2,4,5,6,7,8,9] , [3,10,11,12,13,14,15],1024)
process('restaurants1', 'sample-candset.csv', [1,3,4,5] , [2,6,7,8],128)




######
###### multisplit
######


def processMultisplit(datadir, basename, e1_fields, e2_fields, bflen):
    pool = mp.Pool(processes=4)

    # no maximo 8bits por split
    b = BloomFilter(cap=bflen)
    max_split = round(np.log2(b.bit_size))-2

    ed = encrypt_data(datadir, basename, e1_fields, e2_fields, bflen, set_p=0.5)

    results = [pool.apply_async(parallel_compare_multisplit, args=(ed,s))
               for s in np.arange(1,max_split,1)]
    output = [p.get() for p in results]


    df = output[0]
    for pdf in output[1:]:
        df = df.append(pdf,ignore_index = True)

    # df['diff'] = abs(df.full - df.sbf_sim) * 100
    # ax = df.boxplot('diff',by='p',rot=30)
    df.to_csv(getbase_dir('results')+"msplit_"+datadir+'.csv',sep=';')
    print('Done ' + datadir + "!")

#####
##### comentado
#####

# processMultisplit('bikes', 'candset.csv', [3,4,7] , [8,9,12],96)

# z1 = encrypt_data2('bikes','bikedekho.csv',[1,2,3,4,6,7],96)
# z2 = encrypt_data2('bikes','bikewale.csv',[1,2,3,4,6,7],96)
# len(z2)

# processMultisplit('beer', 'sample-candset.csv', [1,3,4] , [2,5,6],96)
# processMultisplit('books1', 'candset.csv', [1,3,4,5] , [2,6,7,8],256)
# processMultisplit('eletronics', 'sample-candset.csv', [1,4,5,3] , [2,6,7,8],1024)
# processMultisplit('movies1', 'candset.csv', [1,3,4,5] , [2,6,7,8],768)
# processMultisplit('music', 'sample-candset.csv', [2,4,5,6,7,8,9] , [3,10,11,12,13,14,15],1024)
# processMultisplit('restaurants1', 'sample-candset.csv', [1,3,4,5] , [2,6,7,8],128)
