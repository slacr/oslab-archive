#--python--

# The Schedule object is responsible for keeping the execnet cluster workers
# busy, including canceling/rescheduling/duplicating work.

import execnet
import pdb

import m2.workflow.scheduler as base

class Scheduler(base.SchedulerBase):
    ENDMARK_ = object()

    def __init__(self, cluster_manager):
        """Prepare to handle work queued up to be handled by the cluster."""
        super(Scheduler, self).__init__(cluster_manager)

    # def replace_worker_(self, worker, work_entry):
    #     self.logger_.clog("bad worker:" + str(worker))
    #     replacement = super(Scheduler, self).replace_worker_(worker, work_entry)
    #     self.logger_.clog("new worker:" + str(replacement))
    #     return replacement

    def activate_work_(self, uow, worker, channel, work_entry, queue_entry):
        """Do paperwork now that worker has begun work on work_entry."""
        channel.setcallback(self.work_done_callback_(uow, worker, queue_entry.get_callback(), channel),
                            endmarker=Scheduler.ENDMARK_)

    def work_done_callback_(self, uow, worker, cb, channel):
        """Produce a one-time callback closure that invokes the sieve's callback handler."""
        def handle_work_done_closure_(result):
            if result is self.ENDMARK_:
                # channel has closed.  move worker back 
                self.reschedule_worker_(worker, channel)
            else:
                cb(result, channel, uow)

        return handle_work_done_closure_

    def metrics(self):
        return "\n pending_: %s \n pin_ : %s \n" % (str(len(self.pending_)), str(len(self.pin_)))
#        return "\n pending_: %s \n pin_ : %s \n" % (str(len(self.pending_)), self.pin_tostring_())
