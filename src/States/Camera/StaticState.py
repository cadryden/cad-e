'''
Leaves the L{Camera<Utilities.Camera.Camera>} in its current position, not tracking a target.

@author: Chris Alvarado-Dryden
'''
from States.State import State

class StaticState(State):
    """
    Leaves the L{Camera<Utilities.Camera.Camera>} in its current position.  In other words, it does nothing.
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'StaticState')