'''
Keeps the L{Camera<Utilities.Camera.Camera>} centered on its L{Target<Utilities.Camera.Camera.Target>}.

@author: Chris Alvarado-Dryden
'''
from States.State import State
from Utilities.vector import Vector

from Core.Constants import EditorConstants

class TargetState(State):
    """
    Keeps the L{Camera<Utilities.Camera.Camera>} centered on its L{Target<Utilities.Camera.Camera.Target>}, 
    unless prevented by camera collision tiles.
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'TargetState')
       
    def Update(self, dt):
        """
        Centers the L{Camera<Utilities.Camera.Camera>} on its L{Target<Utilities.Camera.Camera.Target>} and checks for camera collision
        tiles.
        """
        oldPos = Vector(self._owner.Position)
        self._owner.Center = self._owner.Target.Center
        newPos = Vector(self._owner.Position)
        
        # reset to original position
        self._owner.Position = oldPos
        
        self._owner.Velocity = (newPos - oldPos) / dt
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(EditorConstants.LAYER_NAME_CAMERA_COLLISION_TILES))