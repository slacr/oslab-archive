#--python--
"""
A execnet module-aware workflow stage.

"""

import execnet

import m2.workflow.stage as base

class SieveBase(base.StageBase):
    def __init__(self, scheduler=None, module=None):
        super(SieveBase, self).__init__(scheduler)
        self.module_ = module
        self.impl_ = __import__(self.module_)

    def get_name(self):
        return self.module_

    def start_work_(self, uow, workflowworker):
        worker = workflowworker.worker()
        try:
            channel = worker.remote_exec(self.impl_)
            self.impl_.start(channel, uow)
            return channel
        except IOError:
            raise base.FailedToStartWork()

    def finish_work_(self, response, channel, uow):
        return self.impl_.finish(response, channel, uow)


    
