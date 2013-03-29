"""Example workflow worker. This particular one uses the powering algorithm
   but all the workers share this functionality."""
import os
import pickle
import time

"""Exception classes for powerfilter()"""
class PowerFilterError(Exception): pass
class OutOfRangeError(PowerFilterError): pass
class NotAnIntegerError(PowerFilterError): pass

primes_pickle_filename = 'primes.pickle'
primes_path = None
primes_file = primes_pickle_filename

try: 
  # python has no defined() primitive, so we try and access __file__
  # and its not defined, we just prepare ourselves to puke.
  primes_path = os.path.dirname(__file__)
  primes_file = os.path.join(primes_path, primes_pickle_filename)
except NameError:
  pass # is this just residue?

def load_pickled_primes():
  try:
    f = open(primes_file, 'rb') # open primes file for reading in binary mode
    primes = pickle.load(f) # read list of primes from file (de-pickle)
    return primes
  except IOError:
    print("Couldn't open initial primes file %s\n", primes_file)
  return [2] # return list [2] on failure

known_primes = None

def get_primes():
  global known_primes
  if known_primes is None:
    known_primes = load_pickled_primes()
  return known_primes

def primes_up_to_n(n):
  index = 0
  primes = get_primes()
  while index < len(primes) and primes[index] <= n:
    yield primes[index]
    index += 1

def split_bits(n):
  """Deterimine the binary representation for a given number

  Calling bit(n) returns a binary representation on a number in string
  format. For example, calling bin(15) returns 0b1111. We get candidate
  prime n, strip off the Ob prefix, turn the list into a string of single
  characters, and map int() over the list to convert everyting to and int.

  Args:
      p: candidate prime

  Returns:
      List of integers representing the number in binary form.

  Raises: Nothing
  """
  # or if J wrote it :)
  # return list(map(int, bin(n)[2::1]))
  bits = bin(n)   # *string* representation of binary characters
  bits = bits[2:] # strip of the 0b in the binary representation
  bit_list = bits[::1] # turn string into list of 1 characters (ugly syntax)
  return list(map(int, bit_list)) # return as a list of ints

def bit_length(x):
  """Count the number o' sig bits in an int."""
  if x < 0:
    raise ValueError("are you serious?")
  return len(bin(x))-2

def isqrt(n):
  """integer-only sqrt."""
  if n < 0:
    raise ValueError("are you serious?")
  if n == 0:
    return 0
  a, b = divmod(bit_length(n), 2)
  x = 2**(a+b)
  while True:
    y = (x + n//x)//2 # integer only division
    if y >= x:
      return x
    x = y

def powering_algorithm(p):
  """Determine if a candidate prime (2**p) can be factored.

  The powering algorithm determines if a candidate prime p can be factored
  by a prime number from 2 to the square root of 2**p. For a quick sanity check
  you can run ./powertest.py. For example, (2**11) - 1 is excluded because
  23 factors it. ((2**11) -1) / 23 = 89. The following example was taken from
  the GIMPs site:

  For example, let's see if 47 divides 2**23-1. Convert the exponent 23 to binary,
  you get 10111. Starting with 1, repeatedly square s, remove the top bit of the
  exponent and if 1 multiply squared value by 2, then compute the remainder upon
  division by 47.

                  Remove   Optional   
    Square (s)     top bit  mul by 2       mod 47
    ------------  -------  -------------  ------
    1*1 = 1       1  0111  1*2 = 2           2
    2*2 = 4       0   111     no             4
    4*4 = 16      1    11  16*2 = 32        32
    32*32 = 1024  1     1  1024*2 = 2048    27
    27*27 = 729   1        729*2 = 1458      1

  Thus, 223 = 1 mod 47. Subtract 1 from both sides. 223-1 = 0 mod 47. Since
  we've shown that 47 is a factor, 2^23-1 is not prime.

  Args:
      p: candidate prime to consider

  Returns:
      p if it is not excluded by the powering algorithm. (p needs to continue
      to the next filter)
      False otherwise

  Raises: Nothing
  """ 
  max_factor = isqrt(2**p)
  if max_factor < 2:
    return p
  for f in primes_up_to_n(max_factor):
    if does_f_factor_p(f, p):
      return False #### can't return enumerated type ####
  else:
    return p

def does_f_factor_p(f, p):
  s = 1 # square mask
  #print(split_bits(p))
  for top_bit in split_bits(p):
    s = s * s 
    #print("top bit equals %d,  s = %d, f = %d, p = %d \n" % (top_bit, s, f, p))
    if top_bit == 1:
      s = s * 2
    s = s % f
  if s == 1: # f factors (2**p), see note above
    #print("Powering Algorithm: excluding %d because %d factors.\n" % (p, f))       
    return True
  else: # went through all factors and none found
    return False

def power_algorithm(remote, p):
  """Do the math calc.

    Returns:
       False if p is not a possible mersenne.
       p if p is potentially a mersenne.
  """
  if p < 5000:
    return p
  # the powering algorithm is slower than llt for p < some number ~5000
  result = powering_algorithm(p)
  return result

""" The following are common to all modules, just with different implementations."""

def remote_handler(request, response):
  """Worker method that generates a response to the given request."""
  conn = request['conn_']
  p = request['p']
  conclusion = power_algorithm(conn, p)
  response['result'] = conclusion

def remote_send_response(channel, response):
  """Pass the results back to the requester."""
  # caller expects a False, or return the p if it factors?.
  # ... which is just what we set in result.
  channel.send(response)

"""
 ****
 Standard Worker API (common to all modules, but each with its own implementation).
 ****
"""

def start(channel, uow):
  """Called by scheduler to trigger a request to a remote worker.

  Pass:
    channel: an execnet Channel to a remote worker.
    uow: a  workflow uow for the tasks at hand.

  Return: Nothing.  """
  request = {
    'p': uow.get_params()
    }
  channel.send(request)

def finish(response, channel, uow):
  """Called by scheduler when result received for uow from channel.

  Pass:
    response: the value send()'ed from remote_send_response()
    channel: the channel to communicate with remote.
    uow: the uow currently being handled.

  Return:
    None, if there is no further work to do
    uow(s) to pass to next sieve.
  Raises:
    RemoteError if something went wrong with worker.
  """
  prime = response['result']
  if prime is False:
    return None
  # uow.refine(prime)  -- if we changed params, we'd do a refine here.
  # if we generated multiple uow for next stage, we'd do splits here
  # to generate the new uow.
  return [ uow ]

# To execute source code remotely this needs to be invoked as an execnet module.
if __name__ == '__channelexec__':
  request = channel.receive()
  request['conn_'] = channel
  response = {
    'started_': time.time(),
    }
  remote_handler(request, response)
  response['stopped_'] = time.time()
  remote_send_response(channel, response)



