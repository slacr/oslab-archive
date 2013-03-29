# The base StateManager classes.
"""
The StateManager is responsible for keeping track of state snapshot files.

All the components in a system register with the StateManager, and when
prompted, the StateManager will gather and store (or recover and reload)
all of the component state.

Components need to provide a unique id, typically their class or instance
name, and register a callback that will (a) provide an object to be
presisted when asked and (b) reset their internal state when provided with
such an object.
"""

import os
import sys
import time

import base
import event
import snapshot

class StateManager(base.StateManagerBase):

    def __init__(self, state_path, namespace=sys.argv[0], version='1_0'):
        super(StateManager, self).__init__()
        self.state_path_ = state_path
        self.namespace_ = namespace
        self.version_ = version
        self.depot_ = os.path.join(self.state_path_, self.namespace_, self.version_)
        self.callbacks_ = {}
        self.initialized_ = False
        self.timepath_ = '%Y-%b-%d-%H-%M-%S'

    def init(self, create=False, safe=True):
        """Prep to handle state under the specified namespace (and given storage version)."""
        if os.path.exists(self.depot_):
            if create and safe:
                raise base.InvalidState()  # don't recreate a dir that exists
        else:
            if not create:
                raise base.InvalidState()
            os.makedirs(self.depot_)
        self.initialized_ = True
        return self

    def register(self, snap_id, callback):
        """Register the supplied callback with the specified namespace id."""
        self.callbacks_[snap_id] = callback

    def unregister(self, snap_id):
        """Remove namespace id from callback list."""
        self.callbacks_[snap_id].clear()

    def get_snaplabel(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        timepath = time.strftime(self.timepath_, time.localtime(timestamp))
        return timepath

    def get_snapshot_path(self, snaplabel=None, timestamp=None):
        """Create the full path to dir to hold the specified snapshot."""
        if snaplabel is None:
            snaplabel = self.get_snaplabel(timestamp)
        snapshot_path = os.path.join(self.depot_, snaplabel)
        return snapshot_path

    def most_recent_snapshot(self):
        """Go to most recently created snapshot dir and get snapshot."""
        cwd = os.getwcd()
        try:
            os.chdir(self.depot_)
            history = sorted(filter(os.path.isdir, os.listdir('.')), 
                             key=lambda d: os.stat(d).st_ctime)
            snap_slot = self.get_statefile_slot_()
            for snaplabel in history:
                os.chdir(snaplabel)
                try:
                    snap = Snapshot(event.events.LOAD).init(snap_slot)
                    if snap.valid():
                        return snaplabel
                finally:
                    os.chdir('..')
            return None
        finally:
            os.chdir(cwd)

    def snapshot(self, snaplabel=None, safe=True):
        """Create a new snapshot directory, then trigger snapshots of all registered agents."""
        print("manager snapshot\n")
        dest = self.get_snapshot_path(snaplabel)
        cwd = os.getcwd()
        try:
            self.hop_to_snaplabel_(dest, safe)
            self.generate_snapshots_()
        finally:
            os.chdir(cwd)

    def restore(self, snaplabel=None):
        """Set the state of things based on the specified snapshot."""
        print("manager restore\n\n")
        if snaplabel is None:
            dest = self.get_snapshot_path(self.most_recent_snapshot())
        else:
            dest = self.get_snapshot_path(snaplabel)
        if not os.path.exists(dest):
            raise base.InvalidState(dest)
        cwd = os.getcwd()
        try:
            print ("validating snapshots\n")
            self.hop_to_snaplabel_(dest, safe=True)
            self.restore_snapshots_()
            print ("validated snapshots\n")
        finally:
            os.chdir(cwd)

    def get_statefile_slot_(self):
        """Create a per-app identifier for the state files."""
        return os.path.basename(sys.argv[0])

    def generate_snapshots_(self):
        """Call all registered agents to create their snapshot files."""
        # assert (.. we are under depot ..)
        snap_slot = self.get_statefile_slot_()
        snap = snapshot.Snapshot(event.events.SAVE).init(snap_slot)
        snap.notify(self.callbacks_)
        snap.save()

    def restore_snapshots_(self):
        """Recover the state for the registered clients."""
        # assert (.. we are under depot ..)
        snap_slot = self.get_statefile_slot_()
        snap = snapshot.Snapshot(event.events.LOAD).init(snap_slot)
        print ("recovering snapshot\n")
        snap.load()
        print ("recovered snapshot\n")
        snap.notify(self.callbacks_)
        print ("restored snapshot\n")

    def hop_to_snaplabel_(self, dest, safe):
        """Safely change to a state-label directory."""
        print('hop_to_snaplabel_:' + str(dest) + ':' + str(safe))
        if os.path.exists(dest) and not safe:
            raise base.DuplicateState(dest)
        if not os.path.exists(dest):
            os.makedirs(dest)
        os.chdir(dest)
