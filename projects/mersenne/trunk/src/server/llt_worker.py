"""API for permforming the Lucas Lehmer primality test"""

import time

"""Exception classes for primes()"""
class LucasLehmerError(Exception): pass
class OutOfRangeError(LucasLehmerError): pass
class NotAnIntegerError(LucasLehmerError): pass

def lucas_lehmer(p):
  """ Implementation of Lucas Lehmer test to determine if a number is prime.

  Given a prime number p, determine if it's a mersenne prime, M, by 
  running the primality test on a remote server. As a side note, primes
  tend to cluster around squares (check on this in the discrete math text).

  The actual code uses the Lucas-Lehmer primality test, which states that
  for p>2, (2**p)-1 is prime if and only if S(p-2) is *zero* in this sequence:

    S(0) = 4
    S(N) = (S(N-1)**2 -2) mod (2**p-1)

  For example, to test if 2**7-1 (the number 127) is prime:
    S(0) = 4
    S1 = (4 * 4 - 2) mod 127 = 14
    S2 = (14 * 14 - 2) mod 127 = 67
    S3 = (67 * 67 - 2) mod 127 = 42
    S4 = (42 * 42 - 2) mod 127 = 111
    S5 = (111 * 111 - 2) mod 127 = 0 

  The caveat: the lucas-lehmer test is very expensive. When we first ran the 
  test on three machines in the cluster (12.05.2011) it took approximately
  50 hours to find the 27th Mersenne number, written M(27). It's important
  to filter as many primes as possible from the list of primes passed to the
  lucas-lehmer test. This filtering is done in primes.py.

  Args:
    p: The prime to consider.

  Returns:
    The Mersenne Prime or False otherwise

  Raises:
    OutOfRangeError on numbers below 2
    NotAnIntegerError on things that ain't integers
  """
  try:
    n = int(p)
  except:
    raise NotAnIntegerError("string found. power_a(p) requires an integer greater 1")
  if int(p) != p:
    raise NotAnIntegerError("lucas_lehmer(p) requires an integer greater 1")
  if p < 2:
    raise OutOfRangeError("lucas_lehmer(p) where n is an integer greater 1")

  S = 4 # initial S(0) value
  M = (1 << p)- 1 # Shift 1 left p times to get 2^p, and then subtract 1
  for i in range(3, p+1): # range(3, p+1) produces [3,4,...p]
    S = (S*S-2) % M # S(i) = (S(i-1) * S(i-1)) - 2 mod M
  if S==0:
    return M
  else:
    return False

def handler_lucas_lehmer(remote, p):
  """Handle a Lucas Lehmer remote procedure call via execnet's remote_exec().

  This handler is called by execnet, so what this function returns depends on
  what execnet expects as the return value. It may be the case that we don't
  need to return anything because it will never be seen by the invoker. The
  invoker can only see what it send()s on the channel.

  Args:
    channel: A handle for an ssh connection in execnet.

    p: The prime to consider.

  Returns:
    False if p is not a mersenne prime.
    M if p is the mersenne prime (2**p)-1

  Raises:
    nothing
  """
  result = lucas_lehmer(p)
  return result

""" The following are common to all modules, just with different implementations."""

def remote_handler(request, response):
  """Worker method that generates a response to the given request."""
  conn = request['conn_']
  p = request['p']
  conclusion = handler_lucas_lehmer(conn, p)
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
    uow: a workflow uow for the tasks at hand.
  Return: Nothing.
  """
  params = uow.get_params()
  request = {
    'p': params['p']
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
  params = uow.get_params()
  M = response['result']
  if M is False:
    return None
  uow.refine({'p': params['p'], 'M': M })  
  return [ uow ] # This is M

# To execute source code remotely this needs to be invoked as an execnet module.
if __name__ == '__channelexec__':
  request = channel.receive()
  request['conn_'] = channel
  response = {
    'started_': time.time()
    }
  remote_handler(request, response)
  response['stopped_'] = time.time()
  remote_send_response(channel, response)



