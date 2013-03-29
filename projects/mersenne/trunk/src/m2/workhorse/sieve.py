#--python--
"""
A workhorse stage that uses execnet-workers to perform the work
and is state-enabled, so it can be paused and restarted.

"""
import execnet

import m2.state as state

import sieve_base as base
import uow

class Sieve(base.SieveBase):
    def __init__(self, state_manager=None, module=None, scheduler=None):
        super(Sieve, self).__init__(scheduler, module)
        self.state_manager_ = state_manager

    def init(self, parent_state_id):
        super(Sieve, self).init()
        self.id_ = "%s.%s" % (parent_state_id, self.module_)
        self.state_manager_.register(self.id_, self.state_callback_)
        return self

    # State management methods (from state/manager.py)
    def state_callback_(self, event, snap_data):
        """Handle state changes from StateManager.

        event = LOAD or SAVE (or puke-and-die if they send something else)
        context = the obj we supplied during registration (a None for now)
        snap_data = for events.LOAD, the snapshot data we returned earlier.
        """
        print("STATE CALLBACK -- SIEVE: " + str(self.module_) + ':' + str(event))
        if event is state.event.events.LOAD:
            if self.running_ or len(self.in_progress_) > 0:
                raise state.InvalidState
            self.restore_(snap_data)
            return snap_data
        elif event is state.event.events.SAVE:
            snap = self.snapshot_()
            return snap
        else:
            raise state.InvalidState

    def snapshot_(self):
        """Freeze our current state, to recover later."""
        print("SNAPSHOT SIEVE: " + str(self.module_))
        incoming = []
        passthru = []
        rejected = []
        # turn in_progress_ back in to incoming_ so they will be rescheduled
        for uow in self.in_progress_:
            incoming.append(uow.snapshot())
        for i in self.incoming_:
            incoming.append(i.snapshot())
        for p in self.passthru_:
            passthru.append(p.snapshot())
        for r in self.rejected_:
            rejected.append(r.snapshot())
        print("snapshot: length of incoming %s:\n" % str(len(incoming)))
        print("snapshot: length of passthru %s:\n" % str(len(passthru)))
        print("snapshot: length of rejected %s:\n" % str(len(rejected)))
        return {
            'incoming': incoming,
            'passthru': passthru,
            'rejected': rejected,
            }

    def restore_uow_(self, state):
        return uow.UnitOfWorkStateful().init().restore(state)

    def restore_(self, snapshot):
        """Recover to state we froze earlier.

        Args:
           snapsot = the state_object returned by prior snapshot_() call.

        Return: (state_object, additions)
        """
        print("RESTORE SIEVE: " + str(self.module_))
        self.incoming_ = []
        self.passthru_ = []
        self.rejected_ = []
        count = 100
        for i in snapshot['incoming']:
            self.add_work(self.restore_uow_(i))
            if count == 0:
                break
            count -= 1
        for p in snapshot['passthru']:
            self.passthru_.append(self.restore_uow_(p))
        for r in snapshot['rejected']:
            self.rejected_.append(self.restore_uow_(r))
        print("restore: length of incoming %s:\n" % str(len(snapshot['incoming'])))
        print("restore: length of passthru %s:\n" % str(len(snapshot['passthru'])))
        print("restore: length of rejected %s:\n" % str(len(snapshot['rejected'])))


    
