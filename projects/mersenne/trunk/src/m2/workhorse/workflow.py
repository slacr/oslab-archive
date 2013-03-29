#--python--
"""
The Workhorse Workflow

This is a workflow designed to work with execnet to run through a series of
calculations.  The results of the prior stage are passed to the next stage
for further computation (or dropped if the prior stage says its no good).

This includes a snap-shot feature which periodically writes the state of the
system out to disk so it can be recovered and used as a launchpad, hopefully
reducing the amount of data which must be recomputed.

"""

import execnet

import m2.workflow.workflow as base
import m2.state as state

import scheduler
import sieve
import uow

class Workhorse(base.WorkflowBase):
    def __init__(self, state_manager, cluster_manager):
        super(Workhorse, self).__init__(scheduler.Scheduler(cluster_manager))
        self.state_mgr_ = state_manager
        self.state_id_ = 'workhorse'

    def init(self,
             assignment_callback=None,
             output_callback=None,
             discard_callback=None,
             low_water_callback=None,
             low_water_mark=0):
        super(Workhorse, self).init(output_callback=output_callback,
                                    assignment_callback=assignment_callback,
                                    discard_callback=discard_callback,
                                    low_water_callback=low_water_callback,
                                    low_water_mark=low_water_mark)
        self.connect_to_state_manager_()
        return self

    def create_stage(self, stage_id):
        stage = sieve.Sieve(state_manager = self.state_mgr_,
                            module = stage_id,
                            scheduler = self.scheduler_).init(self.state_id_)
        assert stage.isrunning() is False
        return stage

    def make_uow_(self, params):
        """ Given an integer prime make_uow_ allocates a new uow """
        return uow.UnitOfWorkStateful().init({'p': params})

    # Additional methods for this class
    def connect_to_state_manager_(self):
        self.state_mgr_.register(self.state_id_, self.state_callback_)

    def metrics(self):
        return """metrics"""+self.scheduler_.metrics()

    # State manager methods
    def state_callback_(self, event, snap_data):
        """Handle state changes from StateManager.

        event = LOAD or SAVE (or puke-and-die if they send something else)
        context = the obj we supplied during registration
        snap_data = for events.LOAD, the snapshot data we returned earlier.
        """
        print("STATE CALLBACK -- WORKFLOW")
        if event is state.event.events.LOAD:
            if self.running_:
                raise state.InvalidState()
            self.restore_(snap_data)
        elif event is state.event.events.SAVE:
            snap = self.snapshot_()
            return snap
        else:
            raise state.InvalidState()

    def snapshot_(self):
        """Freeze our current state, to recover later."""
        print('WORKFLOW SNAPSHOT')
        return {}

    def restore_uow_(self, state):
        return uow.UnitOfWorkStateful().init().restore(state)

    def restore_(self, snapshot):
        """Recover to state we froze earlier.

        Args:
           snapsot = the state_object returned by prior snapshot_() call.

        Return: (state_object, additions)
        """
        print('WORKFLOW RESTORE')
        return snapshot
