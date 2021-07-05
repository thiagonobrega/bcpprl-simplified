import ngram
from lib.mybloom.bloomfilter import *
from lib.mybloom.bloomutil import dice_coefficient

if __name__ == '__main__':
    nome1 = "01/01/1982"
    nome2 = "01/01/1981"

    index = ngram.NGram(N=2)
    bigrams1 = list(index.ngrams(index.pad(nome1)))
    bigrams2 = list(index.ngrams(index.pad(nome2)))
    
#     print bigrams
    
    f1 = BloomFilter(cap=30)
    f2 = BloomFilter(cap=30)
    
    
    for i in bigrams1:
        f1.add(str(i))
    
    
    for i in bigrams2:
        f2.add(str(i))
    
    print(bigrams1)
#     print f1
    print(bigrams2)
#     print f2
# 
#     print 30*"-"
#     f3 = f1.intersection(f2)
#     print f1
#     print f2
#     print f3
    
    print(f1.print_stats())
    print(f1)
    print(f2.print_stats())
    print(f2)
    print(dice_coefficient(f1,f2))