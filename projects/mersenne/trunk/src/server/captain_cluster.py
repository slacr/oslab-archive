#--python

import m2.workflow.cluster as cluster
import m2.workflow.scheduler as scheduler

import primes
import execnet
import heapq
import os
import re       # regular expressions
import socket


class NoWorkersAvailable(Exception): pass


class HeavyWorker(scheduler.WorkflowWorker):
  """A HeavyWorker accepts anything.  Just use the base class for now."""
  pass

class LightWorker(HeavyWorker):
  """A light-duty worker handles everything but the final LLT calculation."""
  is_llt = re.compile('llt_worker');

  def findwork(self, workqueue):
    """Find next non-LLT task """
    i = -1
    sieve = -1
    for i in xrange(len(workqueue)):
      sieve = workqueue[i].get_queue_entry().get_id()
      # print "i: " + str(i)
      if not LightWorker.is_llt.match(sieve):
        # print "not match: " + str(sieve)
        return workqueue.pop(i)
    if len(workqueue):
      # Can't find a non-llt, so just take something...
      return workqueue.pop(0)
    # print "death! at i: " + str(i) + " for: " + str(sieve)
    raise IndexError()

class CaptainCluster(cluster.ClusterManager): 

  def __init__(self):
    super(CaptainCluster, self).__init__()
    self.logger_ = None
    self.gateways_ = []
    self.worker_label_ = None
    self.janitors = None
    self.worker_attrs_ = {}

  def init(self, new_logger):
    super(CaptainCluster, self).init()
    self.logger_ = new_logger
    return self

  def connect_to_execnet_cluster(self, worker_label=None):
    """Make connections to our cluster

    Note: Right now we have the list of hosts hard coded in host-list.ini.
    Eventually we may want to call a helper function generate_host_list(host-file)
    to generate our host list. I'm not sure if that will happen anytime soon
    so we'll hardcode everything in host-list.ini for now.

    Here's what we need to accomplish to be a fair and righteous API.

    1. Create multiple clusters so we can send different kinds of work to
       different clusters. For example, the lab machines act as one cluster,
       the Macintosh machines outside the lab act as another, etc. Right now
       we've only tested the lab cluster and the mac cluster because Windows
       is being testy with ssh connections, which is what execnet uses.
       Apparenlty Windows is popping open an ssh window whenever execnet tries
       to connect. See Isaac if you feel like getting a windows cluster added
       to Captain Cluster. It would help the cause.

    2. Specify the number of connections to establish to each host and create
       the gateways.

    3. Log the connection information in the connections log file.

    4. 'Nice' the processes so we aren't killing the boxes.

    Args:
      clogfile: The connections log file where we log our connection info

    Returns: gws, a list of open execnet connections
      
    Raises: NoWorkersAvailable if no worker connections can be made.
    """ 
    self.worker_label_ = worker_label
    worker_hosts = self.get_host_list(self.worker_label_)

    # sync out primes.primes_file to all the workers.
    rsync = self.prepare_rsync_job()
  
    self.gateways_ = []
    self.janitors_ = execnet.Group()

    for h in worker_hosts:
      attr = self.get_host_attributes(h, self.janitors_, worker_label)
      if not attr["reachable"]:
        self.logger_.clog("\n %s mentioned but not reachable. Ignoring.\n" % (h))
        continue
      if not self.prepare_host(h, worker_label):
        self.logger_.clog("\n %s mentioned but incompatible. Ignoring.\n" % (h))
        continue
      for i in range(attr["max_connections"]):
        self.gateways_.append(self.prepare_new_worker(h, i, rsync))

    connection_count = len(self.gateways_)

    if connection_count:
      self.logger_.clog("\nWe have %d connections\n" % (connection_count))
    else:
      raise NoWorkersAvailable()
    self.do_rsync_files(rsync)

    return self.gateways_

  def prepare_new_worker(self, hostname, worker_id, rsync_job=None):
    """Set a worker up with what it needs to do work."""
    if rsync_job is None:
      rsync = self.prepare_rsync_job()
    else:
      rsync = rsync_job

    host_attrs = self.get_host_attributes(hostname, self.janitors_, self.worker_label_)  # TODO(rename to cluster_attrs or pool_attrs)
    if not host_attrs["reachable"]:
      self.logger_.clog("\n %s mentioned but not reachable. Dying.\n" % (h))
      raise KoboldsAteMyBabies()
    con_id = hostname + str(worker_id)  # host + connection number
    gw = self.create_connection(hostname, con_id, host_attrs['nice'])

    # includes worker in rsync, renames file to be primes_pickle_filename
    rsync.add_target(gw, primes.primes_pickle_filename)

    if rsync_job is None:
      self.do_rsync_files(rsync)

    return gw

  def prepare_rsync_job(self):
    return execnet.RSync(primes.primes_file)

  def do_rsync_files(self, rsync):
    self.logger_.clog("rsyncing primes.primes_file to cluster\n")
    rsync.send()
    self.logger_.clog("rsync'd primes to machines in cluster\n")

  def get_host_list(self, worker_label):
    try:
      host_filename = 'host-list.ini'
      if worker_label:
        host_filename = '%s-%s' % (worker_label, host_filename)
      f = open(host_filename,'r')  # open host list
      hosts = f.read().splitlines()  # reads in hostnames in and removes all \n
      print("hosts:" + str(hosts) + "\n")
    except IOError:
      print("Couldn't open file %s\n", host_filename)
    # return ['osl-psyduck']
    return hosts

  # Now the the processes are smaller because we're dialing down the
  # number of items in each workers queue we may be able to put more
  # connections on the lab machines. (Meaning set ditto and squirtle
  # to True.
  powerful_hosts = {  # handle lots o' connections; for now the macs
    "osl-ditto":False,    # this one only has 4G memory
    "osl-squirtle":False, # as does this one (4G)
    "osl-psyduck":True
    }

  uptime_hosts = { # not likely to reboot; handle llt connections
    "osl-ditto": True,
    "osl-squirtle": True,
    "osl-psyduck": True
    }

  def get_host_attributes(self, hostname, janitors, worker_label):
    powerful_connections = 10 # connections to our badass machines
    pussy_connections = 8  # connections to any other machines
    powerful_nice = 5
    pussy_nice = 15
    nice = pussy_nice
    max_connections = pussy_connections

    if CaptainCluster.powerful_hosts.get(hostname):
      nice = powerful_nice
      max_connections = powerful_connections

    # os.system() returns the process exit status, which is 0 on success and
    # non-zero otherwise. For ping, 0 equals at least one response was heard,
    # 2 if successfully transmitted but no response, and any other non-zero
    # is an error.

    reachable = self.analyze_host(janitors, hostname, worker_label)
    print("reachable: " + str(reachable))
    return {"nice": str(nice), # we need to return a string to concat on gateway
            "max_connections": max_connections,
            "reachable": reachable}

  def prepare_host(self, hostname, worker_label):
    # we want to nuke any old execnet jobs that may be lying
    # around from prior runs using the given worker_label
    # (if one is provided).
    try:
      self.logger_.clog("\n killing all python on %s\n" % (hostname))
      if socket.gethostname() != hostname:
        os.system('ssh %s killall python' % (hostname))
        # TODO(fix this for multiple pools)
      self.logger_.clog("\n killed all python on %s\n" % (hostname))
    except:
      return False
    return True

  def analyze_host(self, janitors, hostname, worker_label):
    """Interrogate a remote host and see if it usable."""
    if hostname[0] == '#':
      # skip hosts that are commented out in hostlist.ini
      self.logger_.clog("\n skipping host %s\n" % (hostname))
      return False  

    try:
      reachable = (os.system('ping -c 1 %s' % (hostname)) == 0)
      if reachable:
        self.logger_.clog("\n creating janitor %s\n" % (hostname))
        cleaner = janitors.makegateway('ssh='+hostname+'//id=janitor//nice=20')
        self.logger_.clog("\n created janitor %s\n" % (hostname))
    except:
      return False
    return reachable

  def create_connection(self, hostname, connection_id, niceness):
    """Create a new connection to a prepared host."""
    gateway_cmd = "ssh="+hostname+"//id="+connection_id+"//nice="+ niceness
    gw = execnet.makegateway(gateway_cmd)
    # keep track of how we created this gw so we can re-create it if necessary.
    self.worker_attrs_[gw] = (hostname, connection_id, niceness)
    return gw

  def total_cluster_size(self):
    return len(self.gateways_)

  def get_all_execnet_connections(self):
    return self.gateways_

  def get_workers(self):
    """Return set of WorkflowWorkers."""
    workflow_workers = []
    for gw in self.gateways_:
      workflow_workers.append(self.make_workflow_worker_(gw))
    return workflow_workers

  def make_workflow_worker_(self, gw):
    """Check connection id and see which host it came from."""
    conn_id = gw.id
    for (host, reliable) in CaptainCluster.uptime_hosts.iteritems():
      if conn_id.startswith(host):
        if reliable:
          self.logger_.clog("\n giving LLT work to : %s\n" % (conn_id))
          return HeavyWorker(gw)
        else:
          self.logger_.clog("\n holding %s off for light duty.\n" % (conn_id))
          return LightWorker(gw)
    self.logger_.clog("\n Defaulting %s to light duty.\n" % (conn_id))
    return LightWorker(gw)

  def replace_worker(self, workflowworker):
    """Create a new worker with same parameters as dead worker.
    
    """
    gateway = workflowworker.worker()
    resume = self.worker_attrs_.pop(gateway)
    self.logger_.clog("\n replacing worker %s \n" % (gateway))
    replacement = self.create_connection(resume[0], resume[1], resume[2])
    self.logger_.clog("\n replaced worker %s  with %s\n" % (gateway, replacement))
    return self.make_workflow_worker_(replacement)


