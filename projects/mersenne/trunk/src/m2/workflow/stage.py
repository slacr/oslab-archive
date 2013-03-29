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

import collections

class NoStages(Exception): pass
class BadStage(Exception): pass
class InvalidInitState(Exception): pass
class NoMoreWork(Exception): pass
class FailedToStartWork(Exception): pass

class StageBase(object):
    """
    This is one of them there abstract classes, which means it isn't fully
    implemented. It needs to be subclassed to complete the definition with
    a concrete class. 
    """
    def __init__(self, scheduler=None):
        self.scheduler_ = scheduler
        self.incoming_ = []
        self.pending_ = []
        self.in_progress_ = []
        self.passthru_ = []
        self.rejected_ = []
        self.running_ = False

    def get_name(self):
        pass

    def init(self, priority=None):
        self.scheduler_.register_queue(self.get_name(),
                                       self.cb_scheduler_start_work_,
                                       self.cb_scheduler_work_done_,
                                       priority)
        return self

    def add_work(self, uow):
        """Add the unit-of-work to the to-do list."""
        self.incoming_.append(uow)
        if self.running_:
            self.scheduler_.add_work(self.get_name(), uow)
        else:
            self.pending_.append(uow)

    def run(self):
        """Dispatch any queued ."""
        self.running_ = True
        if len(self.pending_) > 0:
            for uow in self.pending_:
                self.scheduler_.add_work(self.get_name(), uow)
            self.pending_ = []

    def suspend(self):
        self.running_ = False

    def get_finished(self):
        fini = list(self.passthru_)
        #self.passthru_.clear()
        self.passthru_ = []
        return fini

    def get_rejected(self):
        reject = list(self.rejected_)
        #self.rejected_.clear()
        self.rejected_ = []
        return reject

    def isbusy(self):
        return self.running_ and 0 != (len(self.in_progress_) + len(self.passthru_))

    def isdry(self, level=0):
        return self.running_ and level >= (len(self.incoming_) + len(self.passthru_))

    def isready(self):
        return self.running_ and 0 < (len(self.incoming_)  + len(self.passthru_))

    def isrunning(self):
        return self.running_

    def isidle(self):
        return self.running_ and 0 == (len(self.incoming_) + len(self.passthru_) + len(self.rejected_))

    def cb_scheduler_start_work_(self, worker, uow):
        """Callback method for Scheduler class to let us know to kick-off work.

        Pass:
        worker - the worker chosen to do the work
        uow - unit of work to do.

        Returns: a connection to the work-in-progress.

        throws: FailedToStartWork on worker error.
        """
        self.incoming_.remove(uow)
        self.in_progress_.append(uow)
        try:
            return self.start_work_(uow, worker)
        except FailedToStartWork:
            self.in_progress_.remove(uow)
            self.incoming_.append(uow)
            raise

    def cb_scheduler_work_done_(self, response, channel, uow):
        """Callback method for Scheduler class when unit of work finished.

        Pass:
          result - the result from the module (if any)
          channel - the channel returned from cb_scheduler_work_done_
          uow - unit of work completed.
        """
        self.in_progress_.remove(uow)
        results = self.finish_work_(response, channel, uow)
        if results is None:
            self.rejected_.append(uow)
        else:
            self.passthru_.extend(results)

    def start_work_(self, uow, worker):
        """
        Implementation specific method to begin remote execution of work.

        This is an abstract method. An actual implementation should be done by
        a subclass.

        Pass:
          uow - 
          worker - 

        Returns: a connection to the work-in-progress

        throws: FailedToStartWork on worker error.
        """
        pass

    def finish_work_(self, response, channel, uow):
        """
        Method to clean up the implementation specific end of work overhead.
        

        This is an abstract method. An actual implementation should be done by
        a subclass.
        """
        pass
