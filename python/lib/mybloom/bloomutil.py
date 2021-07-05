'''
Created on 23 de abr de 2016

@author: Thiago
'''
from __future__ import division
from lib.util.data import NullField

def dice_coefficient(filter1 , filter2):
    """ 
        Calculates the dice coeficiente of the two underlyng bloom filter.
        
        filter1 : crypto.mybloom.bloomfilter
        filter2 : crypto.mybloom.bloomfilter
        
        return : number between 0 and 1
    """
    
    if (type(filter1) is NullField) or (type(filter2) is NullField) :
        return 0 
    
    h = filter1.intersection(filter2).filter.count(True)
    a = filter1.filter.count(True)
    b = filter2.filter.count(True)
    return 2*h/(a+b)

def jaccard_coefficient(filter1 , filter2):
    """ 
        Calculates the jaccard index between 2 bloom filters 
        
        filter1 : crypto.mybloom.bloomfilter
        filter2 : crypto.mybloom.bloomfilter
        
        return : number between 0 and 1
    """
    
    if (type(filter1) is NullField) or (type(filter2) is NullField) :
        return 0 
    
    #Brasileiro, i've coded this part using this website [1]
    #Please check this, chunk of code. It may contain error :p
    # 1 -http://blog.demofox.org/2015/02/08/estimating-set-membership-with-a-bloom-filter/
    
    inter = filter1.intersection(filter2).filter.count(True)
    union = filter1.union(filter2).filter.count(True)
    
    if union == 0:
        return 0

    return inter/union