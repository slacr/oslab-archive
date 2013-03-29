#--python--

import enum

events = enum.Enum(['LOAD', 'SAVE'])

class SnapshotEvent(object):
    def __init__(self, event, uniq_id, context, state_manager):
        self.event_ = event
        self.uniq_id_ = uniq_id
        self.context_ = context
        self.state_manager_ = state_manager

class SnapshotSaveEvent(SnapshotEvent):
    def __init__(self, uniq_id, context, state_manager):
        super(SnapshotSaveEvent, self).__init__(events.SAVE, uniq_id, context, state_manager)

class SnapshotLoadEvent(SnapshotEvent):
    def __init__(self, uniq_id, context, state_manager, snapshot):
        super(SnapshotLoadEvent, self).__init__(events.LOAD, uniq_id, context, state_manager)
        self.snapshot_ = snapshot

