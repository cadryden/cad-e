'''
A virtual gamepad with L{Button<Utilities.Controller.Button.Button>}s and a L{DPad<Utilities.Controller.DPad.DPad>}.

@author: Chris Alvarado-Dryden
'''
import os
import pygame
from pygame.locals import *

from Utilities.Controller.Button import Button

class Controller(object):
    """
    A Controller represents a virtual gamepad with L{Button<Utilities.Controller.Button.Button>}s
    and a L{DPad<Utilities.Controller.DPad.DPad>}.  The class handles the conversion between hardware key
    presses and virtual button pushes, so the rest of the game does not need to look to the hardware.
    
    @note:  There are currently several ways to update the Controller, which may be cleaned up in the future.
    
    @type dpad:             L{DPad<Utilities.Controller.DPad.DPad>}
    @ivar dpad:             The directional pad for this gamepad.
    
    @type _buttons:         C{list}
    @ivar _buttons:         List of the L{Button<Utilities.Controller.Button.Button>}s on this Controller.
    
    @type _nameToButton:    C{dict}
    @ivar _nameToButton:    C{{str : L{Button<Utilities.Controller.Button.Button>}}} - Dictionary mapping names to buttons.
    
    @type _bindToButtons:   C{dict}
    @ivar _bindToButtons:   C{{U{keyboard constant<http://www.pygame.org/docs/ref/key.html>} : [L{Button<Utilities.Controller.Button.Button>}, ... ]}} - 
                            Dictionary mapping keyboard constants to a C{list} of buttons. 
    """ 
    def __init__(self, bindingLists, dpad=None):
        """
        Creates a new Controller with new L{Button<Utilities.Controller.Button.Button>}s, and the passed
        L{DPad<Utilities.Controller.DPad.DPad>}.
        
        The constructor will create and hold the buttons using the L{bindingLists} parameter as shown in the example below.
        
        Ex::
            Controller([['Jump', K_SPACE], ['Shoot', K_f]], DPad())
        
        This creates a controller with a jump button bound to the spacebar, a shoot button
        bound to the F key, and a DPad with the default configuration.
        
        @type  bindingLists:    C{list}
        @param bindingLists:    A C{list} of C{list}s, each having a button name, and a then the
                                U{keyboard constants<http://www.pygame.org/docs/ref/key.html>} the button will be bound to.
                                Ex::
                                    C{[['Jump', K_SPACE, K_w], ['Duck', K_s], ['Accept', K_ENTER, K_SPACE]]}
        
        @type  dpad:   L{DPad<Utilities.Controller.DPad.DPad>}
        @param dpad:   The directional pad for this gamepad.  By default, one is not created.
        """
        self._buttons = []
        self._nameToButton = {}
        self._bindToButtons = {}
        
        for bindList in bindingLists:
            name = bindList[0]
            button = Button(name)
            self._buttons.append(button)
            self._nameToButton[name] = button
            
            bindKeys = bindList[1:]
            for bind in bindKeys:
                if (self._bindToButtons.has_key(bind)):
                    self._bindToButtons[bind].append(button)
                else:
                    self._bindToButtons[bind] = [button]
            
        self.dpad = dpad 
    
    @staticmethod
    def ControllerFromXML(path):
        """
        Constructs a C{list} of Controllers from the .XML file at the given path.
        
        For an explanation of the Controller's XML format, check here. [I'll link to something eventually - CAD]
        
        @type  path:    C{str}
        @param path:    Path to the .XML file containing Controller definitions.
        
        @rtype:         C{list}
        @return:        List of new Controllers.
        """
        from Utilities.Controller.ControllerXMLLoader import ControllerXMLLoader
        import xml.sax

        controllers = []

        handler = ControllerXMLLoader(controllers)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(os.path.normpath(os.path.realpath(path)))
                
        return controllers
    
    def UpdateAllEvents(self):
        """
        Updates the state of the L{Button<Utilities.Controller.Button.Button>}s on this Controller.
        
        @note: This function will remove all C{QUIT}, C{KEYDOWN}, and C{KEYUP} C{U{pygame.event<http://www.pygame.org/docs/ref/event.html>}}
        in the event queue after processing.
                
        @rtype:     C{bool}
        @return:    C{False} if a C{QUIT} event is encountered, otherwise returns C{True}.
        """
        quit = False
        for event in pygame.event.get([QUIT, KEYDOWN, KEYUP]):
            quit = self.UpdateEvent(event)
            if (quit):
                return True
        return False
      
    def Button(self, buttonName):
        """
        Gets the L{Button<Utilities.Controller.Button.Button>} object with the given name.
        
        @type  buttonName:    C{str}
        @param buttonName:    The name of a L{Button<Utilities.Controller.Button.Button>} on this Controller.
        
        @rtype:               L{<Utilities.Controller.Button.Button>}
        @return:              The selected button.
        """
        return self._nameToButton[buttonName]
    
    def HasButton(self, buttonName):
        """
        Returns C{True} if the Controller has the L{Button<Utilities.Controller.Button.Button>} with the given
        name, C{False} otherwise.
        
        @type  buttonName:    C{str}
        @param buttonName:    The name of a L{Button<Utilities.Controller.Button.Button>} on this Controller.
        
        @rtype:               C{bool}
        @return:              C{True} if the Controller has a L{Button<Utilities.Controller.Button.Button>}
                              with the given name, C{False} otherwise.
        """
        return self._nameToButton.has_key(buttonName)
        
    def UpdateEvent(self, event):
        """
        Updates the state of the L{Button<Utilities.Controller.Button.Button>}s on this Controller
        using the given event.
        
        @type  event:    C{U{pygame.event<http://www.pygame.org/docs/ref/event.html>}}.
        @param event:    The pygame event to process.
        
        @rtype:          C{bool}
        @return:         C{False} if a C{QUIT} event is encountered, otherwise returns C{True}.
        """
        # Quit conditions
        if(event.type == QUIT):
            return False
        elif (event.type == KEYDOWN and event.key == K_ESCAPE):
            return False
        
        # button presses
        if (event.type == KEYDOWN):
            for bind, buttons in self._bindToButtons.items():
                if (event.key == bind):
                    for button in buttons:
                        button.Down = True
        # button releases
        elif (event.type == KEYUP):
            for bind, buttons in self._bindToButtons.items():
                if (event.key == bind):
                    for button in buttons:
                        button.Down = False

        return True    

    def UpdateEvents(self, events):
        """
        Updates the state of the L{Button<Utilities.Controller.Button.Button>}s on this Controller
        using the given list of events.
        
        @type  events:    C{list}
        @param events:    The C{U{pygame.event<http://www.pygame.org/docs/ref/event.html>}} list to process.
        
        @rtype:           C{bool}
        @return:          C{False} if a C{QUIT} event is encountered, otherwise returns C{True}.
        """
        for button in self.Buttons:
            button.UpdatePreviousState()
        
        for event in events:
            if not self.UpdateEvent(event):
                return False
            
        if (self.dpad):
            return self.dpad.UpdateEvents(events)
        return True;

    def UpdateKeys(self, pressList):
        """
        Updates the state of the L{Button<Utilities.Controller.Button.Button>}s on this Controller
        using the given list of U{key states<http://www.pygame.org/docs/ref/key.html#pygame.key.get_pressed>}.
        
        @type  pressList:    C{list}
        @param pressList:    Boolean key states for each keyboard key.
        """
        # save previous state
        for button in self.Buttons:
            button.UpdatePreviousState()
        
        # clear current state
        for button in self.Buttons:
            button.Up = True
        
        for bind, buttons in self._bindToButtons.items():
            if (pressList[bind]):
                for button in buttons:
                        button.Down = True
            
        if (self.dpad):
            self.dpad.UpdateKeys(pressList)

    def __str__(self):
        """
        The name and state of each of the components on this Controller. 
        
        @rtype:    C{str}
        @return:   String representation of the Controller and its components.
        """
        string = '----------------------\n'
        if (self.dpad):
            string += self.dpad.__str__() + '\n'
        for button in self.Buttons:
            string += button.__str__() + '\n'
        string += '----------------------'
            
        return string
    
    def ToXMLString(self):
        """
        Generates XML to create this Controller.
        
        @rtype:    C{unicode}
        @return:   XML formatted output. 
        """
        string = '<controller>\n'
        for button in self.Buttons:
            binds = []
            for key in self._bindToButtons:
                for b in self._bindToButtons[key]:
                    if b is button:
                        binds.append(key)
            string += button.ToXMLString(binds)
        if (self.dpad):
            string += self.dpad.ToXMLString()
        
        string += '</controller>\n'
        return unicode(string)

    ############### PROPERTIES ###############
    
    def __get_buttons__(self):
        return self._buttons
    Buttons = property(__get_buttons__, None, None, "List of this Controller's L{Button<Utilities.Controller.Button.Button>}s.")