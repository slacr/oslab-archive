#--python--

import time

import enum

Event = enum.Enum(['CREATE', 'INIT', 'RESTORE', 'SAVED', 'REFINE', 'SPLIT', 'DISCARD'])

class UnitOfWork(object):
    """A logical task that works its way through the workflow.

    A UnitOfWork can be split in to mulitple (presumably smaller) units, or it
    can just be dropped (discarded) if there is nothing else to be done for it.
    """
    def __init__(self):
        self.condition_ = None
        self.params_ = {}
        self.tags_ = {}
        self.touched_ = None
        self.created_ = None
        self.worker_ = None
        self.stage_ = None
        self.history_ = []
        self.annotate_(Event.CREATE)

    def init(self, params=None):
        self.annotate_(Event.INIT)
        self.params_ = params
        return self

    def get_params(self):
        """Retrieve current params for unit of work."""
        # expect self.condition_ is not event.CREATE
        return self.params_

    def get_history(self):
        """Retrieve the sequence of past events."""
        return self.history_

    def get_created_time(self):
        return self.created_

    def get_access_time(self):
        return self.touched_

    def isactive(self):
        return (self.condition_ is not None and
                self.condition_ is not Event.CREATE and
                self.condition_ is not Event.DISCARD)

    def isdiscarded(self):
        return (self.condition_ is Event.DISCARD)

    def set_current_worker(self, worker):
        self.worker_ = worker

    def set_current_stage(self, stage):
        self.stage_ = stage

    def get_worker(self):
        return self.worker_

    def get_stage(self):
        return self.stage_

    def refine(self, params):
        """Save prior params, replace with new params."""
        self.annotate_(Event.REFINE, self.params_)
        self.params_ = params

    def discard(self):
        """Mark UoW as completed, but discarded."""
        self.annotate_(Event.DISCARD)
        self.params_ = None

    def split(self, new_params):
        """Split this UoW in to multiple units, preserving history."""
        children = []
        for params in new_params:
            uow = self.deepcopy()
            self.annotate_(Event.SPLIT, self.params_)
            uow.params_ = params
            children.append(uow)
        return children

    def annotate_(self, event, details=None):
        """Update uow's condition and preserve prior state in history."""
        now = time.time()
        if Event.CREATE == event:
            self.created_ = now
        else:
            entry = (now, self.condition_, details)
            self.history_.append(entry)
        self.condition_ = event
        self.touched_ = now
