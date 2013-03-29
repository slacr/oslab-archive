#--python--
"""
Base classes for the Workflow cluster manager.
"""

class ClusterManager(object): 
  def __init__(self):
    pass

  def init(self):
    return self

  def get_workers(self):
    pass

  def replace_worker(self, worker):
    """Replace the provided worker with a new fresh worker.

    Args:
      worker - worker to retire.

    Returns: new worker.

    Raises: KoboldsAteMyBaby if no new worker available...
    """
    pass
