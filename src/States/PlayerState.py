'''
B{[Base Class]} A base class for L{Player<Player.Player>} states that includes a stub function used to process input every frame.

@author: Chris Alvarado-Dryden
'''
from States.State import State

class PlayerState(State):
    """
    B{[Base Class]} A base class for L{Player<Player.Player>} states that includes a stub function used to process input every frame.
    This should be treated like an interface.
    """
       
    def ProcessInput(self):
        """
        B{[Stub]} Processes any L{Controller<Utilities.Controller.Controller.Controller>} input from the L{Player<Player.Player>}.
        """
        return