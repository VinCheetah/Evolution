from functools import reduce
from operator import mul
from numpy import mean, median


def product_aggregation(x):  # note: `x` is a list or other iterable
    return reduce(mul, x, 1.0)


def sum_aggregation(x):
    return sum(x)


def max_aggregation(x):
    return max(x)


def min_aggregation(x):
    return min(x)


def maxabs_aggregation(x):
    return max(x, key=abs)


def median_aggregation(x):
    return median(x)


def mean_aggregation(x):
    return mean(x)