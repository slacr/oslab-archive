#!/usr/bin/python
# main entry point for any init daemon or person who starts this bad boy.

"""
    mersenne.py [-i <seconds>] [-t <label>] [-m <max prime>]
                [-s <stats interval>] <filter> <filter> ...

    Run a workhorse workflow with the worker filter modules, potentially
    starting from the snapshot <label>, snapshotting the progress every <seconds>

    Examples:
    $ python ./mersenne.py powerfilter_worker llt_worker
    $ python ./mersenne.py -i 3600 powerfilter_worker llt_worker
    $ python ./mersenne.py -m 6000 powerfilter_worker llt_worker
    $ python ./mersenne.py -s 10 powerfilter_worker llt_worker
    $ python ./mersenne.py -s 10 -m 6000 powerfilter_worker llt_worker
    $ python ./mersenne.py -i 60 -t 2012-Jan-17-21-32-03 powerfilter_worker llt_worker

  ---
     To get debugging information from execnet run main like this:
        % rm -f /tmp/execnet-debug-*; EXECNET_DEBUG=2 python mersenne.py 
  ---

  Note: Don't forget to use ssh-agent bash and ssh-add before running this.

"""

import sys
sys.path.append("../")

import pdb

import execnet
import getopt
import time

import primes
import logger
import captain_cluster

import m2.workhorse as workhorse
import m2.state as state
import m2.workflow.uow as uow
import m2.workflow.workflow as workflow

class FindMersennePrimes(object):
    state_depot = '../state/'
    log_depot = '../logs/'
    state_namespace = 'mersenne'
    default_low_water_mark = 1

    def __init__(self, logger):
        self.state_manager_ = None
        self.workhorse_ = None
        self.snapshot_interval_ = None
        self.last_snapshot_ = None
        self.metrics_interval_ = None
        self.last_metrics_ = None
        self.logger_ = logger
        self.metrics_ = {
            'cluster_size':0,
            'sieve_count':0,
            'work_assigned':0,
            'work_done':0,
            'work_seen':0,
            'work_dropped':0,
            'workers':{},
            'assigned':{},
            }
        self.mersenne_list_ = [3]
        self.burst_rate_ = None
        self.known_primes_ = None

    def init_execnet(self):
        self.cluster_ = captain_cluster.CaptainCluster().init(self.logger_)
        self.cluster_.connect_to_execnet_cluster()
        self.metrics_['cluster_size'] = self.cluster_.total_cluster_size()  # TODO(make dynamic)

    def init(self, sieves=[], interval=None, metrics_interval=60, burst_rate = 1000):
        self.snapshot_interval_ = interval
        self.metrics_interval_ = metrics_interval
        self.init_execnet()
        self.state_manager_ = state.manager.StateManager(FindMersennePrimes.state_depot).init(create=True, safe=False)
        self.workhorse_ = workhorse.workflow.Workhorse(self.state_manager_, self.cluster_).init(
            output_callback=self.cb_done,
            discard_callback=self.cb_dropped,
            assignment_callback=self.cb_assigned,
            low_water_callback=self.cb_low,
            low_water_mark=10
            )
        self.workhorse_.load_stages(sieves)
        self.metrics_['sieve_count'] = len(sieves)
        self.burst_rate_ = burst_rate
        self.next_prime_ = 0
        return self

    def initialize_primes(self, max_primes=10000000):
        """Generates an initial list of primes using primes.generate_primes(n)

        Args:
          f: File to log info about primes, which for now is just the total number
             or primes.

        Returns: List of primes self.known_primes_

        Raises: nothing  
        """
        self.max_primes_ = max_primes
        self.next_prime_ = 0 # set this back to the beginning of the list

        self.logger_.plog("Initialize primes to %s \n" % (max_primes))
        # our object then builds an array of all the known primes up to max_primes
        self.known_primes_ = primes.generate_primes(max_primes)
        primes.pickle_primes(self.known_primes_)
        self.logger_.plog("Primes found: " + str(len(self.known_primes_)) + "\n")
        return self.known_primes_

    def track_metrics(self, uow, dropped=True):
        self.metrics_['work_seen'] += 1            
        worker_name = str(uow.get_worker().worker())
        worker_metrics = self.metrics_['workers'].get(worker_name, {}) 
        if dropped:
            worker_metrics['work_seen'] = 1+ worker_metrics.get('work_seen', 0)
            worker_metrics['work_dropped']= 1+ worker_metrics.get('work_dropped', 0)
            self.metrics_['work_dropped'] += 1
        else:
            worker_metrics['work_seen'] = 1+ worker_metrics.get('work_seen', 0)
            worker_metrics['work_done']= 1+ worker_metrics.get('work_done', 0)
            self.metrics_['work_done'] += 1

        self.metrics_['workers'][worker_name] = worker_metrics

        # if last-known job for worker was this task, clear out assignment.
        current = self.metrics_['assigned'].get(worker_name, (0, None))
        if current[0] == uow.get_params()['p']:
            self.metrics_['assigned'] = None
        
    def log_metrics(self):
        self.logger_.flog('cluster size: ' + str(self.metrics_['cluster_size']))  # TODO(dynamic)
        self.logger_.flog('sieve count: ' + str(self.metrics_['sieve_count']))
        self.logger_.flog('total work seen: ' + str(self.metrics_['work_seen']))
        self.logger_.flog('total work assigned: ' + str(self.metrics_['work_assigned']))
        self.logger_.flog('total work done: ' + str(self.metrics_['work_done']))
        self.logger_.flog('total work dropped: ' + str(self.metrics_['work_dropped']))
        worker_stats = self.metrics_['workers']

        for worker,stats in worker_stats.iteritems(): # iterate over the worker_stats dict giving keys/values
            self.logger_.flog(worker + ' seen: ' + str(stats.get('work_seen', 0)))
            self.logger_.flog(worker + ' done: ' + str(stats.get('work_done', 0)))
            self.logger_.flog(worker + ' dropped: ' + str(stats.get('work_dropped', 0)))

        for worker in self.cluster_.get_all_execnet_connections():
            current = self.metrics_['assigned'].get(worker, ('Nothing', 'Nothing'))
            self.logger_.clog(str(worker))   # + " status: " + str(worker.remote_status()))
            self.logger_.flog(str(worker) + ' busy with ' + str(current[0]) + '(' + str(current[1]) + ')')
  
        self.logger_.flog(self.workhorse_.metrics())

    def cb_done(self, uow):
        """Handle the output of the final filter."""
        self.track_metrics(uow, dropped=False)

        params = uow.get_params()
        prime = params['p']
        M = params['M']
        
        self.logger_.plog("%s finished: %s\n" % (str(uow.get_worker().worker()), str(params['M'])))
        
        self.mersenne_list_.append(M)
        msg = "Welcome to your 2**%d-1 M: %d" % (prime, M)
        self.logger_.flog(msg)
        self.logger_.flog(str(uow.get_access_time()))
        print(msg)
        M_abbrv = str(M)
        M_digits = len(M_abbrv)
        max_digits_before_abbreviation = 12

        if M > 10**max_digits_before_abbreviation:
            M_abbrv = M_abbrv[0:4] + '...' + M_abbrv[-4:-1]

        msg_fmt = '| {0:2d} | {1:5d} | {2:10} | {3:8d} | {4:14} | {5:14} |'
        msg = msg_fmt.format(len(self.mersenne_list_),
                             prime,
                             M_abbrv,
                             M_digits,
                             str(int(uow.get_access_time() -
                                     uow.get_created_time())),
                             time.strftime("%D %T",
                                           time.gmtime(uow.get_access_time())))
        self.logger_.slog(msg)

    def cb_dropped(self, uow):
        self.track_metrics(uow)
        params = uow.get_params()
        prime = params['p']
        self.logger_.plog("worker %s dropped prime %s\n" % (str(uow.get_worker().worker()), str(prime)))

    def cb_assigned(self, uow):
        params = uow.get_params()
        stage = uow.get_stage()
        prime = params['p']
        self.logger_.plog("assigned worker %s %s(%s)\n" % (str(uow.get_worker().worker()),
                                                           str(stage),
                                                           str(prime)))
        metrics = self.metrics_['assigned']
        metrics[uow.get_worker().worker()] = (prime, stage)

    def cb_low(self):
        self.add_burst_items()
    
    def periodic_snapshot(self):
        if self.last_snapshot_ is None:
            self.last_snapshot_ = time.time()
        now = time.time()
        drift = int(now - self.last_snapshot_)
        if self.snapshot_interval_ and (drift > self.snapshot_interval_):
            self.state_manager_.snapshot()
            self.last_snapshot_ = now

    def periodic_metrics(self):
        if self.last_metrics_ is None:
            self.last_metrics_ = time.time()
        now = time.time()
        drift = int(now - self.last_metrics_)
        if self.metrics_interval_ and (drift > self.metrics_interval_):
            self.log_metrics()
            self.last_metrics_ = now

    def load_from_snapshot(self, when):
        """Restart from a prior snapshot."""
        self.state_manager_.restore(when)

    def get_next_prime(self):
        index = self.next_prime_
        self.next_prime_ += 1
        if index > len(self.known_primes_):
            raise IndexError
        p = self.known_primes_[index]
        if p > self.max_primes_:
            raise IndexError
        return p

    def add_busy_work(self, max_primes):
        """Kick off the workflow from 3..max_primes


        """
        self.initialize_primes(max_primes)
        self.add_burst_items()

    def add_burst_items(self):
        """     A note on xrange: """
        for count in xrange(self.burst_rate_):
            try:
                n = self.get_next_prime()
            except IndexError:
                return
            self.metrics_['work_assigned'] += 1
            self.workhorse_.add_task(n)
        

    def run(self):
        """Enter a loop until wf throws an exception (no more)."""
        self.workhorse_.run()
        try:
            while(True):
                self.workhorse_.heartbeat()
                self.periodic_metrics()
                self.periodic_snapshot()
                time.sleep(0.01)
        except workflow.NoMoreWork:
            self.logger_.plog("Fini.")
            exit(0)
        exit(-1)

def parse_command_line():
    """Read the command line getopt options (and act on them)."""
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "ni:ht:m:s:",
                                   ["dry-run", "interval=", "help", "timestamp=", "max=", "stats="])
    except getopt.error, msg:
        print msg
        print "for help use --help."
        sys.exit(2)
        
    options = {
        'max': 10000000
        }

    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif o in ("-n", "--dry-run"):
            sys.exit(4)  # not yet supported...
        elif o in ("-i", "--interval"):
            options['interval'] = int(a)
        elif o in ("-t", "--timestamp"):
            options['timestamp'] = a
        elif o in ("-m", "--max"):
            options['max'] = int(a)
        elif o in ("-s", "--stats"):
            options['stats'] = int(a)
        else:
            sys.exit(3)  # how did we get here?
    # And what are left as args must be our filter list.
    options['sieves'] = args
    return options

def main():
    options = parse_command_line()

    the_logger = logger.Logger(path=FindMersennePrimes.log_depot).init()
    wf = FindMersennePrimes(the_logger).init(sieves=options['sieves'],
                                             interval=options.get('interval', None),
                                             metrics_interval=options.get('stats', None))
  
    when = options.get('timestamp', False)
#    pdb.set_trace()        
    if when:
        wf.load_from_snapshot(when)
    else:
        wf.add_busy_work(options['max'])
    wf.run()

    the_logger.flog("Iterated through all primes.\n")


# Begin gross python thing: we want to be able to test this file (main.py)
# with unittest. So, we set it up as a package so we can call it and run it
# as itself. 
if __name__ == '__main__':
    main()
            
                                    
                              
                          

                      
