#--python--
import pdb
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

class NoStages(Exception): pass
class BadStage(Exception): pass
class InvalidInitState(Exception): pass
class NoMoreWork(Exception): pass

class WorkflowBase(object):
    def __init__(self, scheduler):
        self.scheduler_ = scheduler
        self.stages_ = []
        self.running_ = False
        self.idle_ = None
        
    def init(self,
             assignment_callback=None,
             output_callback=None,
             discard_callback=None,
             low_water_callback=None,
             low_water_mark=0):
        self.scheduler_.init(assignment_callback)
        self.assignment_cb_ = assignment_callback
        self.output_cb_ = output_callback
        self.discard_cb_ = discard_callback
        self.more_data_cb_ = low_water_callback
        self.more_data_level_ = low_water_mark
        return self

    def clear_stages(self):
        """Discard any and all stages that have already been loaded."""
        if self.running_:
            raise BadStage()   # cannot clear ourselves while we're running.
        for stage in self.stages_:
            stage.stop()
        self.stages_ = []

    def load_stages(self, stages):
        """Given a list of Stage module names, load and initialize them."""
        if self.running_:
            raise BadStage()   # cannot add to ourselves while we're running.
        for name in stages:
            stage = self.create_stage(name)
            assert stage.isrunning() is False
            self.stages_.append(stage)

    def create_stage(self, stage_id):
        pass

    def append_stage(self, stage):
        """Add an stage to the end of the stage waterfall."""
        if self.running_ or stage.isrunning():
            raise BadStage()
        self.stages_.append(stage)

    def run(self):
        """Go live, based on current state."""
        if len(self.stages_) == 0:
            raise NoStages()
        for stage in self.stages_:
            stage.run()

    def pause(self, checksum=True):
        """Stop operations, but don't discard state."""
        for stage in self.stages_:
            assert stage.isrunning() is True
            stage.suspend()

    def add_task(self, params):
        task = self.make_uow_(params)
        self.add_work([task])

    def add_tasks(self, paramses):
        tasks = []
        for params in paramses:
            tasks.append(self.make_uow_(params))
        self.add_work(tasks)

    def make_uow_(self, params):
        return uow.UnitOfWork().init(params)

    def add_work(self, uows):
        """Add to-do work in to the system.

        Manually add work (rather than add work via low-water-mark callback).
        """
        first_stage = self.stages_[0]
        for uow in uows:
            #assert uow is instanceof UnitOfWork
            first_stage.add_work(uow)

    def heartbeat(self):
        """Do one cycle of the workflow's responsibility.

        The 'main loop', if you will, for the workflow.
        """
        # pdb.set_trace()

        rejected = []
        completed_map = {}
        for s in self.stages_:
            completed_map[s] = s.get_finished()
            rejected.extend(s.get_rejected())
        # Reshuffle completed work to next stage.
        self.handle_completed_(completed_map)
        completed_map.clear()
        # Notify caller of any rejected uow's.
        self.handle_rejects_(rejected)
        #rejected.clear()
        rejected = []
        # add pending new work for the stage...
        self.handle_low_water_()
        # look for any more work to be done.
        self.scheduler_.kick_lolligaggers()
        for s in self.stages_:
            if s.isready() or s.isbusy():
                self.idle_ = None
                return
        else:
            if self.idle_ is None:
                for s in self.stages_:
                    if not s.isidle():
                        self.idle_ = False
                        return
                else:
                    self.idle_ = True
                    return
            # all stages empty. we've finished.
            raise NoMoreWork()

    def next_stage_(self, uow, prior_stage):
        """Determine the next step for this uow."""
        next_index = 1 + self.stages_.index(prior_stage)
        if next_index == len(self.stages_):
            return None
        return self.stages_[next_index]

    def handle_low_water_(self):
        if not self.more_data_cb_:
            return
        if self.stages_[0].isdry(level=self.more_data_level_):
            self.more_data_cb_()

    def handle_completed_(self, completed_map):
        # Take finished uow's and either:
        #  a) move them on to the next appropriate stage, or
        #  b) let the caller known we're done with them.
        finished = []
        for (stage, uows) in completed_map.iteritems():
            for uow in uows:
                next_stage = self.next_stage_(uow, stage)
                if next_stage is None:
                    finished.append(uow)
                else:
                    next_stage.add_work(uow)
        for uow in finished:
            self.output_cb_(uow)

    def handle_rejects_(self, rejects):
        # Notify caller of any rejected uow's.
        if self.discard_cb_:
            for reject in rejects:
                self.discard_cb_(reject)
