#--python--
#
# All the components in a system register with the StateManager, and when
# prompted, the StateManager will gather and store (or recover and reload)
# all of the component state.
#
# Components need to provide a unique id, typically their class or instance
# name, and register a callback that will (a) provide an object to be
# presisted when asked and (b) reset their internal state when provided with
# such an object.
#
# Consider the manager to be librarian -- it is the expert in knowing where
# things belong, not necessarily a subject expert.
# The actual knowledge (state) is in a snapshot, which the librarian really
#

import event

class InvalidState(Exception): pass
class CorruptState(Exception): pass
class DuplicateState(Exception): pass

# The base StateManager classes.
#
class StateManagerBase(object):
    def __init__(self):
        super(StateManagerBase, self).__init__()

    def init(self):
        return self

    def register(self):
        pass

    def unregister(self):
        pass

    def get_snapshot_path(self):
        pass

    def most_recent_snapshot(self):
        pass

    def snapshot(self):
        pass

    def restore(self):
        pass
        

#
#  The base Snapshot object.
class InvalidStateOperation(Exception): pass

class SnapshotBase(object):
    # class function(s)

    # object method(s)
    def __init__(self, event):
        super(SnapshotBase, self).__init__()
        self.event_ = event
        self.data_ = {}
        self.valid_ = False

    def init(self):
        return self

    def load(self):
        """Load earlier stored state."""
        if self.event_ is not event.events.LOAD:
            self.valid_ = False
            raise InvalidStateOperation

    def save(self):
        """Stored state."""
        if self.event_ is not event.events.SAVE:
            self.valid_ = False
            raise InvalidStateOperation

    def clear(self):
        """Drop internal representation of state."""
        self.data_ = {}
        self.valid_ = False

    def valid(self):
        """Local state is complete and correct."""
        return self.valid_

    def notify(self, component_cb_map):
        """Call components (supplied by manager), allowing them access to the snapshot data."""
        for component, cb in component_cb_map.iteritems():
            try:
                snap_orig = self.data_.get(component, {})
                snap_new = cb(self.event_, snap_orig)
                self.data_[component] = snap_new
            except:
                print(str(component) + ' threw exception during notify')
                raise
                self.data_[component] = {}
        

    

