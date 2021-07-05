from __future__ import division
import math
import xxhash
import bitarray
import numpy as np

class BloomFilter:

    # BloomFilter(1000, 0.01)
    # A bloom filter with 1000-element capacity and a 1% false positive rate
    def __init__(self, cap=1000, fpr=0.01, bfpower=8, bs=0):

        self.capacity = cap
        self.false_positive_rate = fpr
        self.error_rate = fpr
        self.number_of_elements = 0
        self.potencia = bfpower

        # Make sure the false positive rate is a reasonable value
        if self.false_positive_rate >= 1 or self.false_positive_rate <= 0:
            raise Exception('Invalid value for false positive rate. Must be in the open interval between 0 and 1.')

        # Calculate the number of bits needed for the false positive rate
        # TODO: need to set a bit_size as a multiple of 8
        if bs == 0:
            n = int(math.ceil(self.capacity * math.log(1 / self.false_positive_rate) / math.log(2) ** 2))
            self.bit_size = round(n / bfpower) * bfpower
        else:
            self.bit_size = bs

        # Make sure the bloom filter is not too large for the 64-bit hash
        # to fill up.
        if self.bit_size > 18446744073709551616:
            raise Exception(
                'BloomFilter is too large for supported hash functions. Make it smaller by reducing capacity or increasing the false positive rate.')
            return

        # Calculate the optimal number of hash functions
        self.hash_functions = int(round(self.bit_size * math.log(2) / self.capacity))

        # Build the empty bloom filter
        self.filter = bitarray.bitarray(self.bit_size)
        self.filter.setall(False)

    def set_hashfunction_by_p(self,p):
        self.hash_functions = abs(int(round(math.log(p) * self.bit_size / self.capacity)))

    # Add an element to the bloom filter
    def add(self, element):
        # Make sure it's not full
        if self.number_of_elements == self.capacity:
            raise Exception('Bloom Filter is full.')
            return

        # Run the hashes and add at the hashed index
        for seed in range(self.hash_functions):
            self.filter[ xxhash.xxh64(element, seed=seed).intdigest() % self.bit_size ] = True
        self.number_of_elements += 1


    # Check the filter for an element
    # False means the element is definitely not in the filter
    # True means the element is PROBABLY in the filter
    def check(self, element):
        # Check each hash location. The seed for each hash is 
        # just incremented from the previous seed starting at 0
        for seed in range(self.hash_functions):
            if not self.filter[ xxhash.xxh64(element, seed=seed).intdigest() % self.bit_size ]:
                return False
        # Probably in the filter if it was at each hashed location
        return True
    
    """
        Implentei intercecao e union
    """
    def intersection(self, other):
        """ Calculates the intersection of the two underlying bitarrays and returns
        a new bloom filter object."""
        if self.capacity != other.capacity or \
            self.error_rate != other.error_rate:
            raise ValueError("Intersecting filters requires both filters to have equal capacity and error rate")
        new_bloom = self.copy()
        new_bloom.filter = new_bloom.filter & other.filter
        return new_bloom
    
    def __and__(self, other):
        return self.intersection(other)
    
    def union(self, other):
        """ Calculates the union of the two underlying bitarrays and returns
        a new bloom filter object."""
        if self.capacity != other.capacity or \
            self.error_rate != other.error_rate:
            raise ValueError("Unioning filters requires both filters to have both the same capacity and error rate")
        new_bloom = self.copy()
        new_bloom.filter = new_bloom.filter | other.filter
        return new_bloom

    def __or__(self, other):
        return self.union(other)

    def copy(self):
        """
            Return a copy of this bloom filter.
        """
        new_filter = BloomFilter(self.capacity, self.error_rate)
        new_filter.filter = self.filter.copy()
        return new_filter

    def __str__(self):
        return str(self.filter.to01())

    # For testing purposes
    def print_stats(self):
        print('Capacity '+str(self.capacity))
        print('Expected Probability of False Positive '+str(self.false_positive_rate))
        print('Bit Size '+str(self.bit_size))
        print('Number of Hash Functions '+str(self.hash_functions))
        print('Number of Elements '+str(self.number_of_elements))

    ##################################################################################
    ###
    ### SPLITING BLOOM FILTER
    ###
    ##################################################################################

    def split(self,n=2,p=256):
        # for i in range(0,n):
        lbs = round(self.bit_size/n)
        cap = round(self.capacity/n)
        a = BloomFilter(cap=cap, fpr=self.false_positive_rate, bfpower=p, bs=lbs)
        b = BloomFilter(cap=cap, fpr=self.false_positive_rate, bfpower=p, bs=lbs)
        a.filter = self.filter[0:lbs]
        b.filter = self.filter[lbs:]
        return a,b


    ##################################################################################
    ###
    ### BLOOM FILTER HARDENING
    ###
    ##################################################################################
    def xor_folding(self):
        """
            Returns a XOR-Folding BloomFilter with one folding

            Schnell, R., Borgs, C., & Encryptions, F. (2016). XOR-Folding for Bloom Encryptions for Record Linkage.
        """
        lbs = round(self.bit_size / 2)
        cap = round(self.capacity / 2)

        fold_pos = round( len(self.filter) / 2 )

        a = self.filter[0:fold_pos]
        b = self.filter[fold_pos:]
        # print('======>',self.bit_size,'#',len(a),len(b))

        r = BloomFilter(cap=cap, fpr=self.false_positive_rate, bfpower=self.potencia, bs=lbs)
        r.filter = a.__ixor__(b)
        return r

    def blip(self,f=0.02):
        """
            BLoom-and-flI (BLIP)

            Schnell, R., & Borgs, C. (2017). Randomized Response and Balanced Bloom Filters for Privacy Preserving Record Linkage.
            IEEE International Conference on Data Mining Workshops, ICDMW, 218–224. https://doi.org/10.1109/ICDMW.2016.0038
        """

        lbs = round(self.bit_size * 1)
        cap = round(self.capacity * 1)


        pf = 0.5 * f
        a = self.filter.copy()

        for i in range(0,len(a)):
            if np.random.random() < pf:
                a[i] = not a[i]


        r = BloomFilter(cap=cap, fpr=self.false_positive_rate, bfpower=self.potencia, bs=lbs)
        r.filter = a
        return r

    def bblip(self,f=0.02):
        """
            Balanced BLoom-and-flI (BBLIP)

            Schnell, R., & Borgs, C. (2017). Randomized Response and Balanced Bloom Filters for Privacy Preserving Record Linkage.
            IEEE International Conference on Data Mining Workshops, ICDMW, 218–224. https://doi.org/10.1109/ICDMW.2016.0038

            The deufault value was chosend by the best result presented by the author
        """
        lbs = round(self.bit_size * 2)
        cap = round(self.capacity * 2)

        a = self.filter.copy()
        b = self.filter.copy()
        b.invert()
        c = a + b

        pf = 0.5 * f


        for i in range(0, len(c)):
            if np.random.random() < pf:
                c[i] = not c[i]

        r = BloomFilter(cap=cap, fpr=self.false_positive_rate, bfpower=self.potencia, bs=lbs)
        r.filter = c
        return r


# The seed should be a string
def test_bloom_filter_performance(number_of_elements = 1000000,false_positive_rate = 0.01, number_of_false_positive_tests = 10000, seed = 'Test'):
    # Let the user know it might take a bit
    print('Performing test, this might take a few seconds.')

    # Make a big bloom filter
    bf = BloomFilter(number_of_elements, false_positive_rate)

    # Fill it right up
    for i in range (number_of_elements):
        bf.add(seed+i)

    # Try things we know aren't in the filter
    false_positives = 0
    for i in range (number_of_false_positive_tests):
        if bf.check(seed+'!'+i):
            false_positives += 1

    # Calculate the tested rate of false positives
    tested_false_positive_rate = false_positives/number_of_false_positive_tests

    # Show the results
    bf.print_stats()
    print('')
    print('Number of False Positive Tests '+number_of_false_positive_tests)
    print('False Positives Detected '+false_positives)
    print('Tested False Positive Rate '+tested_false_positive_rate)

