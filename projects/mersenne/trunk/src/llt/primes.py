"""API for generating and filtering primes"""

import os
import math
import pickle

"""Exception classes for primes()"""
class PrimeError(Exception): pass
class OutOfRangeError(PrimeError): pass
class NotAnIntegerError(PrimeError): pass

primes_pickle_filename = 'primes.pickle'
primes_path = None
primes_file = primes_pickle_filename
if __file__:
  primes_path = os.path.dirname(__file__)
  primes_file = os.path.join(primes_path, primes_pickle_filename)

#primes_file = os.path.join(os.path.dirname(__file__), "primes.pickle")

def load_pickled_primes():
  try:
    f = open(primes_file, 'rb') # open primes file for reading in binary mode
    primes = pickle.load(f) # read list of primes from file (de-pickle)
    return primes
  except IOError:
    print("Couldn't open initial primes file %s\n", primes_file)
  return [2] # return list [2] on failure

known_primes = None

def get_known_primes():
  global known_primes
  if known_primes is None:
    known_primes = load_pickled_primes()
  return known_primes

def dump_my_pickle(ps):
  try:
    f = open(primes_file, 'wb') # open primes file for writing in binary mode
    primes = pickle.dump(ps, f) # write primes ps to filehandle f
  except IOError:
    print("Couldn't open initial primes file for writing, %s\n", primes_file)

def generate_primes(n):
  """Generate a list of prime numbers from 2 to n.

  primes is our set of known primes. We iterate from 2 to n+1 and check to see
  if our number x is mutually prime with all of the known primes. If so, it's a
  prime. We check all even numbers on every iteration hoping against all hope
  that they may become prime. Someone fix this.

  Note: The form (operator for x in y) generates a set (similar to map, grep,
  etc., applying operator(x) on every value of y). There's no shortcutting.
  Even if one value will fail the predicate all values of y are evaluated.

  Then all() checks to see if every value in the set is True (i.e., not zero). 

  Args:
  n: Max integer value to consider

  Returns: List of primes from 2 to n

  Raises: 
  OutOfRangeError
  NotAnIntegerError
  """
  c = 0
  try:
    c = int(n)
  except :
    raise NotAnIntegerError("string found. primes(n) requires an integer greater 1")
  if int(n) != n:
    raise NotAnIntegerError("primes(n) requires an integer greater 1")
  if n < 2:
    raise OutOfRangeError("primes(n) where n is an integer greater 1: " + str(n))

  primes = get_known_primes()
  last_known_prime = primes[-1] # last known prime
  if n <= last_known_prime:
    return list(primes_up_to_n(n)) # return all primes less than or equal to n
  print("last_known_prime = %d, n = %d\n" % (last_known_prime, n))
  for x in range(last_known_prime, n+1):
    # print("x = %d, count = %d" %(x, len(primes)))
    if all(x % p for p in primes):
      primes.append(x)

  return primes

def primes_up_to_n(n):
  index = 0
  primes = generate_primes(n)
  while index < len(primes) and primes[index] <= n:
    yield primes[index]
    index += 1

def pickle_primes(ps):
  old_primes = load_pickled_primes()
  if len(ps) > len(old_primes):
    dump_my_pickle(ps)

def modular_restrictions_primes(ps):
  """Filters a list of primes using the modular restriction algorithm.
  
  Modular restrictions on Mersenne divisors. Fermat discovered and used the first
  part of this theorem (p = 1 modulo q) and Euler discovered the second.
 
  One very nice property of Mersenne numbers is that any factor q of 2^P-1 must
  be of the form 2kp+1. Furthermore, q must be 1 or 7 mod 8.

  Theorem: Let p and q be odd primes. If p divides Mq, then 
  p = 1 (mod q) and p = +/-1 (mod 8).

  Example: Suppose p divides M(31), then p = 1 or 63 (mod 248).

  Args:
     ps: List of primes

  Returns:
    List of primes filtered using the modular restriction algorithm

  Raises: nothing
      """
  pass
