from __future__ import division
import math
import bitarray
import hashlib

"""
    This bloom filters use only n hash function (md5,sha1,sha256), it's a bit slower than bloomfilter...
    
    If you need better perfomance user bloomfilter
"""
class BloomFilter:

    # BloomFilter(1000, 0.01)
    # A bloom filter with 1000-element capacity and a 1% false positive rate
    def __init__(self, cap=1000, fpr=0.01):

        self.capacity = cap
        self.error_rate = fpr
        self.number_of_elements = 0

        # Make sure the false positive rate is a reasonable value
        if self.error_rate >= 1 or self.error_rate <= 0:
            raise Exception('Invalid value for false positive rate. Must be in the open interval between 0 and 1.')

        # Calculate the number of bits needed for the false positive rate
        self.bit_size = int(math.ceil( self.capacity*math.log(1/self.error_rate) / math.log(2)**2 ))

        # Make sure the bloom filter is not too large for the 64-bit hash
        # to fill up.
        if self.bit_size > 18446744073709551616:
            raise Exception('BloomFilter is too large for supported hash functions. Make it smaller by reducing capacity or increasing the false positive rate.')
            return

    

        # Build the empty bloom filter
        self.filter = bitarray.bitarray(self.bit_size)
        self.filter.setall(False)


    # Add an element to the bloom filter
    def add(self, element):
        # Make sure it's not full
        if self.number_of_elements == self.capacity:
            raise Exception('Bloom Filter is full.')
            return

        # Run the hashes and add at the hashed index
        for gi in g(element,self.bit_size):
            self.filter[gi] = True
        self.number_of_elements += 1


    # Check the filter for an element
    # False means the element is definitely not in the filter
    # True means the element is PROBABLY in the filter
    def check(self, element):
        # Check each hash location. The seed for each hash is 
        # just incremented from the previous seed starting at 0
        for gi in g(element,self.bit_size):
            if not self.filter[gi]:
                return False
        return True
    
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

    # For testing purposes
    def print_stats(self):
        print('Capacity '+self.capacity)
        print('Expected Probability of False Positive '+self.error_rate)
        print('Bit Size '+self.bit_size)
        print('Number of Hash Functions 2')
        print('Number of Elements '+self.number_of_elements)
    
    def __str__(self):
        return str(self.filter)
    

def g(data, l):
    """Calculate the gx() fromblah

     For details see: 
    """
    values = []
    data = data.encode('utf-8')
    h1 = hashlib.sha1(data).hexdigest()
    h2 = hashlib.md5(data).hexdigest()
    
    
    for i in range(2):        
        gi = ( int(h1,16) + i * int(h2,16) ) % l
        values.append(gi)
    
    return values

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

