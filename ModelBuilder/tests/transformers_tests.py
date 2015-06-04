from nose.tools import *
import twxeety.vectorizer as vectorizer
import numpy
from scipy.sparse import csr_matrix


#added twitter features
def test_merge_csr_numpy():
    '''Test for merger of csr array with numpy array'''
    #TODO: Add test for error when dimensions don't match
    a = csr_matrix(numpy.zeros((2,2)))
    b = numpy.zeros((2,2))
    c = vectorizer.mergeCSRwithNumpyArrays(a,b)
    d = numpy.zeros((2,4))
    assert_equal(c.toarray().all(),d.all())

