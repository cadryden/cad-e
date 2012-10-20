'''
A single button for a L{Controller<Utilities.Controller.Controller.Controller>}.

@author: Chris Alvarado-Dryden
'''

class Button(object):
    """
    A single button for a L{Controller<Utilities.Controller.Controller.Controller>}.
    It has a name, and can be either up or down.
    
    @type _name:        C{str}
    @ivar _name:        Name of the button.
    
    @type _isDown:      C{bool}
    @ivar _isDown:      Up/Down state of the button.  C{True} if it's down, C{False} if it's up.
    
    @type _wasDown:     C{bool}
    @ivar _wasDown:     Previous state of the button.  C{True} if was down, C{False} if was up.
    """

    def __init__(self, name='UNAMED'):
        """
        Creates a button with the provided name.  The button defaults to up.
        
        @type  name:   C{str}
        @param name:   The name of the button. Usually used to identify a particular button in a list.
        """
        self._name = name
        self._isDown = False
        self._wasDown = True
    
    def UpdatePreviousState(self):
        """
        Updates the previous state of this button.
        """
        self._wasDown = self._isDown
        
    def __str__(self):
        """
        String description of the current state. 
        
        @rtype:    C{str}
        @return:   "Button I{name} is I{state}."
        """
        if self.Down:
            state = 'DOWN'
        else:
            state = 'UP'
            
        if self._wasDown:
            prevState = 'DOWN'
        else:
            prevState = 'UP'
            
        str = 'Button ' + self._name + ' was: ' + prevState + ' is: ' + state
        
        return str
    
    def ToXMLString(self, binds):
        """
        Generates XML to create this Button.
        
        @type  binds:    C{list}
        @param binds:    List of C{U{keyboard constant<http://www.pygame.org/docs/ref/key.html>}} bound to this
                         Button.
        
        @rtype:          C{unicode}
        @return:         XML formatted output. 
        """
        string = "<button name='" + self._name +"'>\n"
        for key in binds:
            string += "<key>" + str(key) + "</key>\n"
        
        string += '</button>\n'
        return string
    
    ############### PROPERTIES ###############
    
    def __is_up__(self):
        """
        @rtype: C{bool}
        """
        return not self._isDown
    def __set_up__(self, isUp):
        """
        @type isUp:    C{bool}
        """
        self._isDown = not isUp
    def __is_down__(self):
        """
        @rtype: C{bool}
        """
        return self._isDown
    def __set_down__(self, isDown):
        """
        @type isDown:    C{bool}
        """
        self._isDown = isDown
    def __pressed__(self):
        """
        @rtype:     C{bool}
        """
        return ((not self._wasDown) and self._isDown)
    def __released__(self):
        """
        @rtype:     C{bool}
        """
        return (self._wasDown and (not self._wasDown))
    def __is_held__(self):
        """
        @rtype:     C{bool}
        """
        return (self._wasDown and self._isDown)
    
    Up = property(__is_up__, __set_up__, None, "If the button is up.")
    Down = property(__is_down__, __set_down__, None, "If the button is down.")
    Pressed = property(__pressed__, None, None, "If the button was pressed this frame.")
    Released = property(__released__, None, None, "If the button was released this frame.")
    Held = property(__is_held__, None, None, "If the button was held down the last two frames.")