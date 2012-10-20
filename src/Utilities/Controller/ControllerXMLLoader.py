"""
Processes XML files to create  L{Controller<Utilities.Controller.Controller.Controller>}s.

@author: Chris Alvarado-Dryden
"""

from xml.sax.handler import ContentHandler

from Utilities.Controller.DPad import DPad
from Utilities.Controller.Controller import Controller

class ControllerXMLLoader(ContentHandler):
    """
    Processes XML files to create  L{Controller<Utilities.Controller.Controller.Controller>}s.  For
    more information on how XML files are used with CAD-E, go I{here} (eventually - CAD).
    
    @type _controllers:    C{list}
    @ivar _controllers:    List to populate with L{Controller<Utilities.Controller.Controller.Controller>}s.
    
    @type _buttonName:     C{str}
    @ivar _buttonName:     Name from the C{button} tag currently being processed.
    
    @type _binds:          C{list}
    @ivar _binds:          Bindings used to construct the current L{Controller<Utilities.Controller.Controller.Controller>}.
    
    @type _keys:           C{list}
    @ivar _keys:           List of key constants in the current C{button} tag.  See U{here<http://www.pygame.org/docs/ref/key.html>}
                           and L{here<Game>} for their definitions.
    
    @type _getKeys:        C{bool}
    @ivar _getKeys:        C{True} if inside a C{key} tag, C{False} otherwise.
    
    @type _dpad:           L{DPad<Utilities.Controller.DPad.DPad>}
    @ivar _dpad:
    """

    def __init__(self, controllers):
        """
        Create a new U{C{ContentHandler}<http://docs.python.org/library/xml.sax.handler.html>} to process XML nodes.
        
        @type  controllers:    C{list}
        @param controllers:    List to populate with L{Controller<Utilities.Controller.Controller.Controller>}s.
        """

        self._controllers = controllers
        
        self._buttonName = ''
        self._binds = []
        self._keys = []
        self._getKeys = False
        self._dpad = None
        
    def startElement(self, name, attrs):
        """
        Handles starting tags of new elements.  Sets instance variables according to the newly encountered
        element.
        
        @type  name:    C{unicode}
        @param name:    Name of the element.
        
        @type  attrs:   C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:   Attributes of the element.
        """
        if name == 'button':
            self._buttonName = attrs.get('name')
        elif name == 'key':
            self._getKeys = True
        elif name == 'dpad':            
            self._dpad = DPad(int(attrs.get('up')), int(attrs.get('down')), int(attrs.get('left')), int(attrs.get('right')))
        
    def endElement(self, name):
        """
        Handles ending tags of elements.  Creates objects now that the necessary data has been gathered.
        
        @type  name:    C{unicode}
        @param name:    Name of the element.
        """
        if name == 'controller':
            binds = [self._binds]
            
            if self._dpad:
                binds.append(self._dpad)
                
            self._controllers.append(Controller(*binds))
            self._binds = []
            self._dpad = None
        elif name == 'button':
            l = [self._buttonName]
            for k in self._keys:
                l.append(k)
            self._binds.append(l)
            self._keys = []
        elif name == 'key':
            self._getKeys = False
        
    def characters(self, chars):
        """
        Process the data between C{key} tags to create keyboard bindings.
        
        @type  chars:   C{unicode}
        @param chars:   Characters encountered between tags.
        """
        if self._getKeys:
            self._keys.append(int(chars))