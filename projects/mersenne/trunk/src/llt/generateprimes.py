#!/usr/bin/python
"""Script to generate primes and pickle the results

  TODO:
    - add python's equivalent of getoptlong to this thing so we can 
      pass command line options.

  This script is a driver for primes.py. It takes an integer
  from the command line, opens a log file, and calls generate_primes.
  Additionally the script logs the number of primes returned, the
  total number of primes in primes.pickle, and the highest prime.

  This functionality is needed so we can generate primes in the background
  whenever we want. tail -f log-pickle-primes to see how big SOME_BIGASS_NUMBER
  needs to be to add primes to primes.pickle. 

    ./generateprimes.py SOME_BIGASS_NUMBER

  Args:
    n: generate primes up to n

  Returns: list of primes, for no particular reason xxx
 
  Raises: IOError if the file doesn't open
  """ 
import os
import time
import sys
import primes
import console_trigger

# We're using console_trigger, which lets us send a SIGUSR1 signal to cause the
# program to break to a python console so we can see what's going on. Call
# listen() here so we can break in later.
console_trigger.listen()

# nice to 10
os.system('renice %d -p %d' % (10, os.getpid()))

def usage():
    print("./generateprimes <integer>, integer greater than 3")
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

def generate_primes_to_n(n):
    known_primes = primes.load_pickled_primes()
    ps = primes.generate_primes(n)
    if len(ps) > len(known_primes):
        known_primes = ps
    f.write("----------------------------------------\n")
    f.write("Date: " + time.strftime('%m-%d-%Y @ %H:%M') + "\n")
    f.write("Number of primes generated = %d \n" % (len(ps)))
    f.write("Highest prime in primes.pickle = %d \n" % (known_primes[-1]))
    f.write("Number of  primes in primes.pickle = %d \n\n\n" % (len(known_primes)))
    f.flush()
    primes.pickle_primes(ps)
    f.flush()
    f.close()
    return ps

if (len(sys.argv) != 2):
    usage()

n = int(sys.argv[1])

if n != int(n):
    usage()

# open a log file for appending
picklelog = "log-pickle-primes"
f = open_logfile(picklelog)

result =  generate_primes_to_n(n)
print("\nGenerated %d primes up to n=%d. Please see %s for more information\n"
      % (len(result), n, picklelog))
