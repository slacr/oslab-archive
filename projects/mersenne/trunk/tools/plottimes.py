#!/usr/bin/python

"""Generate data needed for graphing primality tests

  Our goal is to produce graphs that illustrate the performance
  of the various primality tests we perform when searching for
  Mersenne Primes. Some of the tests are rumored to perform better
  on smaller primes but choke on larger primes. By logging timing
  we hope to determine which tests are faster and on what range of
  numbers.

  The output of this script can be in pretty much any format. For
  now it outputs the date format accepted by matplotlib, which uses
  a single floating point number format that makes no damn sense.

"""
import os
import time
import sys
from src.llt import primes
from src.llt import llt
from matplotlib.dates import date2num
from datetime import datetime

os.system('renice %d -p %d' % (10, os.getpid()))

def usage():
    print("./lltplot.py <integer>, integer greater than 3")
    exit()

def open_logfile(logname):
  """ Open a file or error if there's an issue

  Args:
    filename: file to open

  Returns: f, file handle
 
  Raises: IOError if the file doesn't open
  """ 
  try:
    f = open(logname,'a') # open file for appending
  except IOError:
    print("Couldn't open file %s\n", logname)
  return f

# need the graph to be standardized
llt_graph_data = "../logs/plot-data/log-llt-graph-data-" + time.strftime('%d-%H-%M')
f = open(llt_graph_data, 'a')

def generateLLTGraphData(n):
    """Generates timing data for the Lucas Lehmer test
    Args: 
        n: generate primes up to n

    Returns:
        ps: list of primes generated

    Raises: nothing
    """
    ps = primes.generate_primes(n)
    for p in ps:
        llt.lucas_lehmer(p)
        # Format the date string depending on what graphing application to
        # use. I'm testing matplotlib which a floating point number for dates
        # and times.
        # f.write("%d %s\n" % (p, time.strftime('%d%H%M%S')))
        time = date2num(datetime.now())
        #f.write("%d %s\n" % (p, time))
        f.write("%s\n" % (time))
        f.flush()
    f.close()
    return ps

if (len(sys.argv) != 2):
    usage()

n = int(sys.argv[1])

if n != int(n):
    usage()

result = generateLLTGraphData(n)
print("\nGenerated plot data for %d primes up to n=%d and logged to %s.\n"
      % (len(result), n, llt_graph_data))




