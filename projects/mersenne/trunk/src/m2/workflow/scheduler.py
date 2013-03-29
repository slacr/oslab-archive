#--python--
"""
Base classes for the Workflow workflow manager.

Each tasks to be done is encapulsated in a UnitOfWork (uow.py)

The featured actors include:
   Stages --  a single transformation done to a uow
   Workflow -- the managing object which moves uow from stage to stage
   Scheduler -- a helper object which farms out uow to a pool of workers

Each Stage keeps track of the assigned uow's, which are being worked on and which aren't, and provides the initial instructions to a worker when a uow gets scheduled.  Post-processing of the worker's results is also handled by the Stage.

The Workflow manages the Stages and passes completed uow's on to the next stage, or if an uow is rejected, discards it after sending any requested notification.

The Scheduler keeps track of workers, and when they are finished, notifies the proper stage and then reschedules the worker for more work.  The Scheduler can, conceivably, do things like automatically retry uow that fail, or schedule uow to multiple workers (if there idle workers) to help overcome system faults.
"""

import heapq
""" A heap queue is physically a list but logically an ordered binary tree with the
    smallest element at the root of the treee/list. We use this as an efficient 
    priority queue. We want to push something into the proper place in the list,
    and always pop the most important thing. """

import itertools

import pdb

import stage

class NoStages(Exception): pass
class BadStage(Exception): pass
class InvalidInitState(Exception): pass
class NoMoreWork(Exception): pass
class BadWorker(Exception): pass

class QueueEntry(object):
    """Our ledger entry for an active work queue of tasks."""
    def __init__(self, queue_id, do_it_cb, result_cb, priority):
        # note: rearranged order so simple sorting of tuples preserves priority.
        # ie, first sort by queue, then sort by priority.
        self.entry_ = (queue_id, priority, do_it_cb, result_cb)

    def get_id(self):
        return self.entry_[0]

    def get_callback(self):
        return self.entry_[-1]

    def get_handler(self):
        return self.entry_[-2]

    def get_priority(self):
        return self.entry_[-3]

class WorkEntry(object):
    """Our ledger entry for a specific unit-of-work to be done."""
    def __init__(self, uow, queue, task_id):
        self.entry_ = (task_id, uow, queue)

#    def __lt__(self, other):
#        return self.__cmp__(other) < 0
        
    def __cmp__(self, other):
        """ Custom compare function. 

        In heapq "highest priority" is the 'least' element, i.e. heapq[0]
        is always the highest priority.

        If you visualize a heapq as an series of numbers from left to
        right, we want the left-most entry to be the highest priority,
        and within equal priority, the left-most entry to be the oldest
        unit of work (using id as age).

        A complication is that our queue_entries assign higher numbers
        to more important queues, so we need to reverse our queue ordering.

        With heapq's use of __cmp__(self, other), the interpretation is:
            return <0 if self comes before other
            return =0 if the same priority
            return >0 if other comes before self

        This means to get a lexical ordering of A versus B, where A is
        numerically greater than B but should be considered lexically
        lesser, we can reverse the sense of cmp by either:
           return __cmp__(B, A)     // swap order of parameters
        or:
           return - (__cmp__(A, B))   // negate the result

        So, when ordering by priority we want to reverse the sense
        of priority (priority 6 is more important than priority 3),
        while we want to preserve the order of id-age (id 11 is more
        important than id 111).
        """
        our_priority = self.get_queue_entry().get_priority()
        their_priority = other.get_queue_entry().get_priority()

        by_urgency = cmp(their_priority, our_priority)

        our_age = self.get_id()
        their_age = other.get_id()

        by_age = cmp(our_age, their_age)

        if by_urgency == 0:
            result = by_age
        else:
            result = by_urgency

#        print("%s: %s %s,  %s %s (%s, %s)" % (str(result),
#                                               str(our_priority),
#                                               str(our_age),
#                                               str(their_priority),
#                                               str(their_age),
#                                               str(by_urgency),
#                                               str(by_age),
#                                               ))
        return result

    def get_id(self):
        return self.entry_[0]

    def get_queue_entry(self):
        return self.entry_[-1]

    def get_uow(self):
        return self.entry_[-2]


class WorkflowWorker():
    """The expected baseclass for all workers.

    The workflow scheduler would like to put very little obligation on the
    worker objects, but it does have one: it must know how to have the worker
    examine a queue of UnitOfWorks and pick one to work on.

    It would be nice to use a Mixin, maybe even Multiple Inheritance, but
    because we can't predict how the connection objects are being constructed
    we'll have to work with composition because that's failsafe.
    """
    def __init__(self, worker):
        self.worker_ = worker

    def worker(self):
        return self.worker_

    def findwork(self, workqueue):
        """Identify a WorkEntry to work on, starting from the end of workqueue.

        The base WorkflowWorker isn't picky and always takes the next one.
        Remember: the workqueue is a heapq -- treat it like one.
        """
        return heapq.heappop(workqueue)


class SchedulerBase(object):
    def __init__(self, cluster_manager):
        """Prepare to handle work queued up to be handled by the cluster."""
        # arrange workers
        self.cluster_manager_ = cluster_manager
        self.idle_workers_ = []
        self.busy_workers_ = []
        self.pending_ = []
        workers = self.cluster_manager_.get_workers()
        for worker in workers:
            if not isinstance(worker, WorkflowWorker):
                raise BadWorker('Workers must be of WorkflowWorker class')
            self.idle_workers_.append(worker)
        self.wcount_ = len(self.idle_workers_)
        # prepare for in/out work queues
        self.qcounter_ = itertools.count()
        self.pin_ = []
        self.pcounter_ = itertools.count()

    def init(self, assignment_callback):
        self.queues_ = {}
        self.assignment_cb_ = assignment_callback
        return self

    def register_queue(self, queue_id, handler, cb, priority=None):
        """Add a named work queue to the scheduler.

        handler: function(worker, uow) - returns connection
        cb: function(....)

        """
        qcount = self.qcounter_.next()
        if priority is None:
            priority = qcount
        queue_entry = QueueEntry(queue_id, handler, cb, priority)
        self.queues_[queue_id] = queue_entry

    def add_work(self, queue_id, uow):
        """Add work for a queue to do."""
#        if self.wcount_ != (len(self.idle_workers_) + len(self.busy_workers_)):
#            pdb.set_trace()
#            print('hmmm')
        queue_entry = self.queues_[queue_id]
        work_count = self.pcounter_.next()
        work_entry = WorkEntry(uow, queue_entry, work_count)
        heapq.heappush(self.pin_, work_entry)  # push on priority queue
        if 0 == (work_count % 1000):
            print("task count = %d" % work_count)
#            print(self.pin_tostring_())
        self.kick_lolligaggers()
#        if self.wcount_ != (len(self.idle_workers_) + len(self.busy_workers_)):
#            pdb.set_trace()
#            print('hmmm')

    def kick_lolligaggers(self):
        """Hand out any uow to the idle workers."""
        no_work = []
        try:
            workqueue = self.pin_
            workqueue.sort()
            while len(self.idle_workers_) > 0:
                idler = self.idle_workers_[0]
                try:
                    workentry = None
                    workentry = idler.findwork(workqueue)
                except IndexError:
                    if len(workqueue) == 0:
                        break  # no more work, leave idle
                if workentry:
                    self.schedule_work_(workentry, idler, workqueue)
                else:
                    no_work.append(idler)
        finally:
            self.pin_ = workqueue
            heapq.heapify(self.pin_)

                
        self.idle_workers_.extend(no_work)

    def schedule_work_(self, work_entry, worker, workqueue):
        try:
            self.idle_workers_.remove(worker)
        except IndexError:
            heapq.heappush(workqueue, work_entry)
            print "no idle workers, continue\n"
        else:
            try:
                worker = self.give_work_to_worker_(worker, work_entry)
            except:
                raise # ------
                print "failed to give work to worker, continue\n"
                heapq.heappush(workqueue, work_entry)
                self.idle_workers_.append(worker)

    def reschedule_worker_(self, worker, channel):
        """Called on notification of remote worker done callback."""
        self.busy_workers_.remove(worker)
        self.pending_.remove(channel)
        self.idle_workers_.append(worker)

    def give_work_to_worker_(self, worker, work_entry):
        uow = work_entry.get_uow()
        uow.set_current_worker(worker)
        queue_entry = work_entry.get_queue_entry()
        uow.set_current_stage(queue_entry.get_id())
        stage_handler = queue_entry.get_handler()
        try:
            channel = stage_handler(worker, uow)  # worker.remote_exec(handler, uow)
            try:
                self.activate_work_(uow, worker, channel, work_entry, queue_entry)
            except:
                raise
            else:
                # add to queues before setting callback, as results might
                # already be pending, and we expect our queues to be properly formed.
                self.busy_workers_.append(worker)
                self.pending_.append(channel)
                self.assignment_cb_(uow)
        except stage.FailedToStartWork:
            # The worker we selected is toast. The scheduler knows this worker is
            # no longer doing work so we gotta pass the torch to another machine
            # in the cluster.
            worker = self.replace_worker_(worker, work_entry)

        return worker

    def replace_worker_(self, worker, work_entry):
        replacement = self.cluster_manager_.replace_worker(worker)
        return self.give_work_to_worker_(replacement, work_entry)  # recurse...
        # TODO(Here is where we'll deal with uow-of-death.)
        
    def pin_tostring_(self):
        msg = ''
        entries = list(self.pin_)
        while len(entries) > 0:
            entry = heapq.heappop(entries)
            msg += "(%s[%s], %s[%s])" % (str(entry.get_queue_entry().get_id()),
                                     str(entry.get_queue_entry().get_priority()),
                                     str(entry.get_id()),
                                     str(entry.get_uow().get_params()['p']))
        return "\n %s \n" % (msg)

    def activate_work_(self, uow, worker, channel, work_entry, queue_entry):
        """Actual implementation provided by subclass."""
        pass

    
