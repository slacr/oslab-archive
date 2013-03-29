#--python--
#
# A Snapshot is supposed to encapsulate the state for a single binary.
# It represents a directory, and all the individual files necessary to preserve
# that executable's state.
#
# It is primarily responsibility is the serialization format of the data on disk.
#
# In this instance, the on-disk format is a single pickle file per registered
# component.
#

import os
import time

import base
import event as events
import pickle

class Snapshot(base.SnapshotBase):

    # object method(s)
    def __init__(self, event):
        super(Snapshot, self).__init__(event)
        self.mode_ = 'wb'
        if event is events.events.LOAD:
            self.mode_ = 'rb'
        self.valid_ = False

    def init(self, snap_slot):
        self.slot_ = snap_slot
        try:
            if self.event_ is events.events.LOAD:
                if not os.path.exists(snap_slot):
                    raise base.InvalidState()
                if not os.path.isdir(snap_slot):
                    raise base.CorruptState()
                self.known_components_ = os.listdir(snap_slot)
            else:   # events.events.SAVE:
                if os.path.exists(snap_slot):
                    raise DuplicateState()                
                os.mkdir(snap_slot)
                self.known_components_ = []
        except:
            raise
            raise base.CorruptState()
        self.valid_ = True
        return self

    def load(self):
        super(Snapshot, self).load()
        for component in self.known_components_:
            print "component = %s\n" % (str(component))
            self.load_component_(component)
        self.valid_ = True

    def load_component_(self, component):
        """ Load a component, in our case a sieve"""
        component_path = self.component_path_(component)
        try:
            print "loading component\n"
            self.data_['load_timestamp_'] = time.time()
            fh = open(component_path, self.mode_)
            self.data_[component] = pickle.load(fh)
            print "loaded component\n"
        except:
            raise
            self.valid_ = False
            raise base.CorruptState()

    def save(self):
        super(Snapshot, self).save()
        def skip_trail_underscore(x):
            return x[-1] != '_'
        for component in filter(skip_trail_underscore, self.data_.keys()):
            self.save_component_(component)
        self.valid_ = True

    def save_component_(self, component):
        component_path = self.component_path_(component)
        try:
            fh = open(component_path, self.mode_)
            pickle.dump(self.data_[component], fh)
            self.data_['save_timestamp_'] = time.time()
        except:
            raise
            self.valid_ = False
            raise base.CorruptState()

    def component_path_(self, component):
        return os.path.join(self.slot_, component)

    def clear(self):
        super(Snapshot, self).clear()
        self.data_ = {}
        self.valid_ = True

    def valid(self):
        super(Snapshot, self).valid()
        return self.valid_
    

