import pkg_resources
import cppyy
import random

cppyy.cppdef(
"""
#define MOCOS_CPPYY
#include "{0}"
#include "{1}"
""".format(
pkg_resources.resource_filename("mocos_helper", "cpp_code/weighted_sampling.h"),
pkg_resources.resource_filename("mocos_helper", "cpp_code/mocosMath.h")
))

cppyy.load_library(pkg_resources.resource_filename("mocos_helper", "cpp_code/libMocosHelper.so"))

from cppyy.gbl import Sampler, std

def sample_with_replacement(weights, to_sample):
    '''Weighted sampling with replacement

    Given an interable (preferably cppyy's std.vector<double>, others will be converted)
    samples to_sample indexes, according to the weights. Weights are proportional, 
    and need not sum to 1.

    Returns list of tuples: (index, number if times selected)

    For example:

    sample_with_replacement([0.0001, 0.9, 0.1, 0.000001], 100) might produce:
    [(1, 91), (2, 9)]
    '''

    if type(weights) != std.vector("double"):
        weights = std.vector("double")(weights)
    sampler = Sampler(weights, to_sample)
    while sampler.advanceToNextConfiguration():
        yield (sampler.index(), sampler.count())

def sample_set(items, weights, to_sample):
    if type(weights) != std.vector("double"):
        weights = std.vector("double")(weights)
    sampler = Sampler(weights, to_sample)

    while sampler.advanceToNextConfiguration():
        what = items[sampler.index()]
        for _ in range(sampler.count()):
            yield what

def randomly_split_list(L, howmuch):
    '''Randomly splits L into two sublists, second containing howmuch elements,
    and the first one the rest.

    L is consumed in the process. The elements are placed on their lists in
    undefined order.

    Example: split_list([1,2,3,4,5,6,7,8,9,10], 3) may return:
    ([8,1,2,10,9,5,4], [6,3,7])
    '''
    inverse = False
    if len(L)/2 < howmuch:
        inverse = True
        howmuch - len(L) - howmuch
        assert howmuch >= 0

    ret = []
    for _ in range(howmuch):
        idx = random.randint(0, len(L)-1)
        ret.append(L[idx])
        L[idx] = L.pop()

    if inverse:
        return ret, L
    else:
        return L, ret

def nonreplace_sample(iterable, howmany):
    '''Perform sampling without replacement from iterable. Number of selected
    elements is min(len(iterable), howmany). Example:

    nonreplace_sample(range(10), 5) may return:
    [4, 7, 2, 1, 9]'''

    ret = []
    iterator = iterable.__iter__()
    try:
        while len(ret) < howmany:
            ret.append(next(iterator))
    except StopIteration:
        return ret

    howmany -= 1

    try:
        while True:
            x = next(iterator)
            ret[random.randint(0, howmany)] = x
    except StopIteration:
        return ret

if __name__ == "__main__":
    # Example usage
    for idx, count in sample_with_replacement([0.3, 0.2, 0.5], 100):
        print("Index:", idx, "selected", count, "times.")
