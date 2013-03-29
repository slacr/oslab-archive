#!/usr/bin/python

"""Pass primes to the various filters to get some basic performance numbers"""

from src.llt import primes
from src.llt import llt
from src.llt import powerfilter
import time

""" Powering Algrorithm benchmarks """

def timelltM17():
    """Time M(17), p = 2281"""
    p = 2281
    result = llt.lucas_lehmer(p)

def timelltM18():
    """Test M(18), p = 3217"""
    p = 3217
    result = llt.lucas_lehmer(p)

def timelltM19():
    """Test M(19), p = 4253"""
    p = 4253
    result = llt.lucas_lehmer(p)

def timelltM22():
     """Test M(22), p = 9941"""
     p = 9941
     result = llt.lucas_lehmer(p)

def timelltM23():
     """Test M(23), p = 11213"""
     p = 11213
     result = llt.lucas_lehmer(p)

""" Powering Algrorithm benchmarks """

def timePowerM17():
    """Time M(17), p = 2281"""
    p = 2281
    result = powerfilter.powering_algorithm(p)

def timePowerM18():
    """Time M(18), p = 3217"""
    p = 3217
    result = powerfilter.powering_algorithm(p)

def timePowerM19():
    """Time M(19), p = 4253"""
    p = 4253
    result = powerfilter.powering_algorithm(p)

def timePowerM22():
    """Time M(22), p = 9941"""
    p = 9941
    result = powerfilter.powering_algorithm(p)

def timePowerM23():
    """Time M(23), p = 11213"""
    p = 11213
    result = powerfilter.powering_algorithm(p)


if __name__ == '__main__':
    from timeit import Timer

    """ Powering Algorithm: M(17), M(18), M(19), M(22), M(23) """

    t = Timer("timePowerM17()", "from __main__ import timePowerM17")
    print("Powering Algorith, M(17), p = 2281 , time = %s\n" % (t.timeit(5)))

    t = Timer("timePowerM18()", "from __main__ import timePowerM18")
    print("Powering Algorith, M(18),  p = 3217, time = %s\n" % (t.timeit(5)))

    t = Timer("timePowerM19()", "from __main__ import timePowerM19")
    print("Powering Algorith, M(19), p = 4253, time = %s\n" % (t.timeit(5)))

    t = Timer("timePowerM22()", "from __main__ import timePowerM22")
    print("Powering Algorith, M(22), p = 9941, time = %s\n" % (t.timeit(5)))

    t = Timer("timePowerM23()", "from __main__ import timePowerM23")
    print("Powering Algorith, M(23) p = 11213, time = %s\n" % (t.timeit(5)))

    """ LLT: M(17), M(18), M(19), M(22), M(23) """

    t = Timer("timelltM17()", "from __main__ import timelltM17")
    print("LLT Algorithm, M(17), p  = 2281, time = %s\n" % (t.timeit(5)))

    t = Timer("timelltM18()", "from __main__ import timelltM18")
    print("LLT Algorithm, M(18), p  = 3217, time = %s\n" % (t.timeit(5)))

    t = Timer("timelltM19()", "from __main__ import timelltM19")
    print("LLT Algorithm, M(19), p  = 4253, time = %s\n" % (t.timeit(5)))

    t = Timer("timelltM22()", "from __main__ import timelltM22")
    print("LLT Algorithm, M(22), p  = 9941, time = %s\n" % (t.timeit(5)))

    t = Timer("timelltM23()", "from __main__ import timelltM23")
    print("LLT Algorithm, M(23), p  = 11213, time = %s\n" % (t.timeit(5)))
