#--python--

import m2.workflow.uow as base

class UnitOfWorkStateful(base.UnitOfWork):
    """A UoW that can suspend and resume itself."""

    def __init__(self):
        super(UnitOfWorkStateful, self).__init__()

    def snapshot(self):
        """Make a snapshot of our state."""
        self.annotate_(base.Event.SAVED)
        return {
            'condition': self.condition_,
            'params': self.params_,
            'tags': self.tags_,
            'touched': self.touched_,
            'created': self.created_,
            'history': self.history_,
            'stage': self.stage_,
            'worker': None,
            }

    def restore(self, state):
        """Set up state based on earlier snapshot()'ed state."""
        self.condition_ = state.get('condition', None)
        self.params_ = state.get('params', None)
        self.tags_ = state.get('tags', None)
        self.touched_ = state.get('touched', None)  
        self.created_ = state.get('created', None)
        self.history_ = state.get('history', None)
        self.stage_ = state.get('stage', None)
        self.worker_ = state.get('worker', None)
        self.annotate_(base.Event.REFINE, state)
        return self
