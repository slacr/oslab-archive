# a sample workflow.
import sys
sys.path.append("../..")

import pdb

import execnet
import getopt
import time

import m2.workhorse as workhorse
import m2.state as state
import m2.workflow.uow as uow
import m2.workflow.workflow as workflow

class FindMersennePrimes(object):
    state_depot = './state/'
    state_namespace = 'sample'
    default_low_water_mark = 1

    def __init__(self):
        self.state_manager_ = None
        self.workhorse_ = None
        self.snapshot_interval_ = None
        self.last_snapshot_ = None

    def init_execnet(self):
        self.cluster_ = [
            execnet.makegateway('popen//id=Foo'),
            execnet.makegateway('popen//id=Bar'),
            ]

    def init(self, sieves=[], interval=None, start_at=None):
        self.snapshot_interval_ = interval
        self.init_execnet()
        self.state_manager_ = state.manager.StateManager(FindMersennePrimes.state_depot).init(create=True, safe=False)
        self.workhorse_ = workhorse.workflow.Workhorse(self.state_manager_, self.cluster_).init(
            output_callback=self.cb_done,
            discard_callback=self.cb_dropped,
            )
        self.workhorse_.load_stages(sieves)
        if start_at is not None:
            if start_at == 0:
                last_snapshot = self.state_manager_.most_recent_snapshot()
                start_at = last_snapshot.when()
            self.state_manager_.load(start_at)
        return self

    def cb_done(self, uow):
        x = uow.get_params()
        print("finished: %s\n" % str(x))

    def cb_dropped(self, uow):
        x = uow.get_params()
        print("dropped: %s\n" % str(x))

    def periodic_snapshot(self):
        if self.snapshot_interval_ is None:
            return
        if self.last_snapshot_ is None:
            self.last_snapshot_ = time.time()
        now = time.time()
        drift = int(now - self.last_snapshot_)
        if drift > self.snapshot_interval_:
            print('trying to snapshot')
            self.state_manager_.snapshot()
            self.last_snapshot_ = now

    def load_from_snapshot(self, when):
        """Restart from a prior snapshot."""
        self.state_manager_.restore(when)

    def add_busy_work(self):
        for n in range(3,101):
            self.workhorse_.add_task(n)

    def run(self):
        """Enter a loop until wf throws an exception (no more)."""
        self.workhorse_.run()
        try:
            while(True):
                self.workhorse_.heartbeat()
                self.periodic_snapshot()
        except workflow.NoMoreWork:
            print "Fini."
            exit(0)
        exit(-1)

def parse_command_line():
    """sample.py [-i <seconds>] [-t <label> ] <filter> <filter> ...

    Run a workhorse workflow of the filter.py files, potentially
       starting from the snapshot <label>
       snapshotting the progress every <seconds>

    Examples:
        $ python ./sample.py -i 60 -t 2012-Jan-17-21-32-03 powerfilter_worker llt_worker

    """
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "ni:ht:",
                                   ["dry-run", "interval=", "help", "timestamp="])
    except getopt.error, msg:
        print msg
        print "for help use --help."
        sys.exit(2)

    options = {}

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
        else:
            sys.exit(3)  # how did we get here?
    # And what are left as args must be our filter list.
    options['sieves'] = args
    return options

def main():
    options = parse_command_line()

#    pdb.set_trace()

    wf = FindMersennePrimes().init(sieves=options['sieves'],
                                   interval=options.get('interval', None))

    when = options.get('timestamp', False)

    if when:
        wf.load_from_snapshot(when)
    else:
        wf.add_busy_work()
    wf.run()

if __name__ == '__main__':
    main()
            
                                    
                              
                          

                      
