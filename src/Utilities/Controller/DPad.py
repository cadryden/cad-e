'''
A 4 directional L{Controller<Utilities.Controller.Controller.Controller>}, with Up, Down, Left, and Right
L{Button<Utilities.Controller.Button.Button>}s.

@author: Chris Alvarado-Dryden
'''
from pygame.locals import *
from Utilities.vector import Vector

from Core import Constants

from Utilities.Controller.Controller import Controller

class DPad(Controller):
    """
    A 4 directional L{Controller<Utilities.Controller.Controller.Controller>}, with Up, Down, Left, and Right
    L{Button<Utilities.Controller.Button.Button>}s.  The DPad is designed to be used with Controllers and is
    not meant to be used by itself.
    
    @note:    In the near future this will be changed to more closely resemble a hardware gamepad.  Probably via one or more
    parent classes defining directional input, and dpads, and this being a keyboard dpad.
    """

    def __init__(self, bindUp=K_UP, bindDown=K_DOWN, bindLeft=K_LEFT, bindRight=K_RIGHT):
        """
        Binds the given keys to the Up, Down, Left, and Right directions.
        If no keys are given they default to the corresponding arrow keys.
        
        Ex::
        
            DPad(K_w, K_s, K_a, K_d)
                    
        Creates a WASD controlled DPad
        
        @type  bindUp:        C{U{keyboard constant<http://www.pygame.org/docs/ref/key.html>}}
        @param bindUp:        Key to be bound to Up
        
        @type  bindDown:      C{U{keyboard constant<http://www.pygame.org/docs/ref/key.html>}}
        @param bindDown:      Key to be bound to Down
        
        @type  bindLeft:      C{U{keyboard constant<http://www.pygame.org/docs/ref/key.html>}}
        @param bindLeft:      Key to be bound to Left
        
        @type  bindRight:     C{U{keyboard constant<http://www.pygame.org/docs/ref/key.html>}}
        @param bindRight:     Key to be bound to Right 
        """
        Controller.__init__(self, [('DPad Up', bindUp), ('DPad Down', bindDown), ('DPad Left', bindLeft), ('DPad Right', bindRight)])
  
    def ToXMLString(self):
        """
        Generates XML to create this DPad.
        
        @rtype:    C{unicode}
        @return:   XML formatted output. 
        """
        
        binds = {}
        
        for key in self._bindToButtons:
            if self._bindToButtons[key][0] is self.Button(Constants.ControllerConstants.DPAD_UP):
                binds['up'] = key
            elif self._bindToButtons[key][0] is self.Button(Constants.ControllerConstants.DPAD_DOWN):
                binds['down'] = key
            elif self._bindToButtons[key][0] is self.Button(Constants.ControllerConstants.DPAD_LEFT):
                binds['left'] = key
            elif self._bindToButtons[key][0] is self.Button(Constants.ControllerConstants.DPAD_RIGHT):
                binds['right'] = key
                
        string = '<dpad '
        string += "up='" + str(binds['up'])  + "' "
        string += "down='" + str(binds['down']) + "' "
        string += "left='" + str(binds['left']) + "' "
        string += "right='" + str(binds['right']) + "'"
        
        string += '/>\n'
        return string
  
    ############### PROPERTIES ###############
        
    def __get_unit_vector__(self):
        v = Vector((0, 0))
        
        if self.Up.Down:
            v += (0, -1)
        if self.Down.Down:
            v += (0, 1)
        if self.Left.Down:
            v += (-1, 0)
        if self.Right.Down:
            v += (1, 0)
            
        return v.safe_normalised()
    
    def __get_up__(self):
        return self._nameToButton[Constants.ControllerConstants.DPAD_UP]
    def __get_down__(self):
        return self._nameToButton[Constants.ControllerConstants.DPAD_DOWN]
    def __get_left__(self):
        return self._nameToButton[Constants.ControllerConstants.DPAD_LEFT]
    def __get_right__(self):
        return self._nameToButton[Constants.ControllerConstants.DPAD_RIGHT]
    
    Direction = property(__get_unit_vector__, None, None, 'The unit L{Vector<Utilities.vector.Vector>} for the direction the DPad is pushed.' )
    Up = property(__get_up__, None, None, 'Button for the Up direction on the DPad.')
    Down = property(__get_down__, None, None, 'Button for the Down direction on the DPad.')
    Left = property (__get_left__, None, None, 'Button for the Left direction on the DPad.')
    Right = property(__get_right__, None, None, 'Button for the Right direction on the DPad.')