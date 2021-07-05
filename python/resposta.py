import pandas as pd

from encrypt import encryptData, encrypt_data_in_memory
from splitting_bf.evaluation import split_bf
from lib.mybloom.bloomutil import jaccard_coefficient


def local_encrypt(df,atts,bfsize,sample_size=500):
    if sample_size == 0:
        return encrypt_data_in_memory(df,atts,bfsize)
    else:
        return encrypt_data_in_memory(df.sample(sample_size),atts,bfsize)


###### contar

def contar(tmp_c,i,sigma):
    try:
        dict_s = tmp_c[i]
        #recuperando a contagem
        try:
            tmp_c[i][sigma] += 1
        except KeyError:
            tmp_c[i][sigma] = 1
    except KeyError:
        tmp_c[i] = {sigma: 1}
        
    return tmp_c


def processar_encriptado_original(t,n_splits):
    tmp_c = {} # estrutura de contagem

    
    for s in t:
        split_id = s[0]
        splits = split_bf(s[1],n_splits)
        previous_sigma = []

        for i in range(0,int(len(splits))):
            local_c = {}
            sigma = splits[i].filter

            if len(previous_sigma) == 0:
                tmp_c = contar(tmp_c,i+1,sigma.to01())
                previous_sigma=sigma
            else:
                previous_sigma = previous_sigma + sigma
                tmp_c = contar(tmp_c,i+1,previous_sigma.to01())
    
    # sumarizando
    cdf = []
    for s in tmp_c:
        cdf.append((s,len(tmp_c[s])))
    
    cdf = pd.DataFrame(cdf)
    cdf.columns = ['split','unique']
    return cdf

def processar_encriptado(t,n_splits,limite=4):
    tmp_c = {} # estrutura de contagem
    cdf = []
    
    splits = split_bf(t[0][1],n_splits)
#     for i in range(0,int(len(splits)/limite)):
    for i in range(0,int(limite)):
        local_c = {}
        
        for s in t:
            split_id = s[0]
            splits = split_bf(s[1],n_splits)
            
            sigma = []
            for j in range(0,i+1):
                if len(sigma) == 0:
                    sigma = splits[j].filter
                else:
                    sigma = sigma + splits[j].filter
            
            local_c = contar(local_c,i,sigma.to01())

            
        cdf.append((i+1,len(local_c[i])))
    
    cdf = pd.DataFrame(cdf)
    cdf.columns = ['split','unique']
    return cdf

def first_question(df,atts,bfsize,n_splits=6,limite=4,sample_size=500):
    df=local_encrypt(df,atts,bfsize,sample_size=sample_size)
    return processar_encriptado(df,n_splits,limite=limite)

def first_question_blocado(df1,df2,atts,bfsize,n_splits=6,limite=4,sample_size=500):
    a1=local_encrypt(df1,atts,bfsize,sample_size=sample_size)
    b1=local_encrypt(df1,atts,bfsize,sample_size=sample_size)
    return processar_encriptado(df,n_splits,limite=limite)

### Segunda questao
def comparar_second_question(df1,df2,atts,bfsize,n_splits=6):
    edf1=local_encrypt(df1,atts,bfsize,sample_size=0)
    edf2=local_encrypt(df2,atts,bfsize,sample_size=0)
    
    result = []
    
    for e1 in edf1:
        id1 = e1[0]
        bf1 = e1[1]
        for e2 in edf2:
            id2 = e2[0]
            bf2 = e2[1]
            
            
            #BBF parts
            bbf1_parts = split_bf(bf1,n_splits)
            bbf2_parts = split_bf(bf2,n_splits)
            
            #XBF
            xbf1_parts = []
            xbf2_parts = []
            try:
                xbf1 = bf1.copy().xor_folding()
                xbf1_parts = split_bf(xbf1,n_splits)
                xbf2 = bf2.copy().xor_folding()
                xbf2_parts = split_bf(xbf2,n_splits)
            except ValueError:
                print('XBF - VE')
            except ZeroDivisionError:
                print('XBF - ZD')
                
            #BLIP
            ibf1_parts = []
            ibf2_parts = []
            try:
                ibf1 = bf1.copy().blip()
                ibf1_parts = split_bf(ibf1,n_splits)
                ibf2 = bf2.copy().blip()
                ibf2_parts = split_bf(ibf2,n_splits)
            except ValueError:
                print('XBF - VE')
            except ZeroDivisionError:
                print('XBF - ZD')
            
            #######
            ## processando
            #######
            #
            # CABECALHO
            out = {'id_a': id1, 'id_b': id2}
            #BBF LINE
            out_bbf = out.copy()
            out_bbf['bf'] = 'bbf'
            out_bbf['full_sim'] = jaccard_coefficient(bf1, bf2)
            #XBF LINE
            out_xbf = out.copy()
            out_xbf['bf'] = 'xbf'
            out_xbf['full_sim'] = jaccard_coefficient(xbf1, xbf2)
            #BLIP LINE
            out_ibf = out.copy()
            out_ibf['bf'] = 'blip'
            out_ibf['full_sim'] = jaccard_coefficient(ibf1, ibf2)
            
            for i in range(0,len(bbf1_parts)):
                ### BBF
                out_bbf['part_'+str(i+1)+'_sim'] = jaccard_coefficient(bbf1_parts[i], bbf2_parts[i])
                ###
                if len(xbf1_parts) == 0:
                    out_xbf['part_'+str(i+1)+'_sim'] = -1
                else:
                    out_xbf['part_'+str(i+1)+'_sim'] = jaccard_coefficient(xbf1_parts[i], xbf2_parts[i])
                ### BLIB
                if len(ibf1_parts) == 0:
                    out_ibf['part_'+str(i+1)+'_sim'] = -1
                else:
                    out_ibf['part_'+str(i+1)+'_sim'] = jaccard_coefficient(ibf1_parts[i], ibf2_parts[i])
                    
            #fim do for
            result.append(out_bbf)
            result.append(out_xbf)
            result.append(out_ibf)
                
                

                
    df = pd.DataFrame(result)
    return df


####

def verificar_distancias(bdf,split_number=16,limiar = 0.7,alfa = 0.1):
#     bdf = df[df.bf == 'bbf']
    
    beta = limiar - alfa
    distancia = 0

    saida = []
    #
    for a in bdf['id_a'].unique():

        distanciais_locais = []
        
        for row in bdf[bdf.id_a == a].iterrows():
            #procura a disntancia de a
            for i in range(4,split_number+4):
                #ta errado se tiver uma no meio tem que parar
                if row[1][i] >= beta:
                    distancia = i - 3
                else:
                    #nao repassa a split
                    break

                distanciais_locais.append(distancia)

        if len(distanciais_locais) == 0:
            dist = 1
        else:
            dist = max(distanciais_locais)
            
        saida.append({'id_a' : a, 'distancia' : dist})

    return pd.DataFrame(saida)

## para quando nao da para armazenar os dados na memoria da maquina
def comparar_second_question_rt(df1,df2,atts,bfsize,n_splits=6,limiar = 0.7,alfa = 0.1):
    edf1=local_encrypt(df1,atts,bfsize,sample_size=0)
    edf2=local_encrypt(df2,atts,bfsize,sample_size=0)
    
    beta = limiar - alfa
    distancia = 0

    saida = []
    
    for e1 in tqdm(edf1,leave=False):
        
        id1 = e1[0]
        bf1 = e1[1]
        
        distanciais_locais = []
        for e2 in tqdm(edf2,leave=False):
            id2 = e2[0]
            bf2 = e2[1]
            
            #BBF parts
            bbf1_parts = split_bf(bf1,n_splits)
            bbf2_parts = split_bf(bf2,n_splits)
            
            #######
            ## processando
            #######
            for i in range(0,len(bbf1_parts)):

#                 jaccard_coefficient(ibf1_parts[i], ibf2_parts[i])
#                 jaccard_coefficient(xbf1_parts[i], xbf2_parts[i])
                if jaccard_coefficient(bbf1_parts[i], bbf2_parts[i]) >= beta:
                    distancia = i+1
                else:
                    #nao repassa a split
                    break

                distanciais_locais.append(distancia)
             #############################################
        
        #fim do for 2
        if len(distanciais_locais) == 0:
            dist = 1
        else:
            dist = max(distanciais_locais)
            
        saida.append({'id_a' : id1, 'distancia' : dist})
                
    return pd.DataFrame(saida)