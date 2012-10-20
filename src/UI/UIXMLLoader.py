'''
Processes XML files to create L{Widgets<UI.Widget.Widget>}s.

@author: Chris Alvarado-Dryden
'''
from xml.sax.handler import ContentHandler

from Utilities.HelperFunctions import ReflectionFunctions

class UIXMLLoader(ContentHandler):
    """
    Processes XML files to create L{Widgets<UI.Widget.Widget>}s.  Inherits from
    U{xml.sax.handler<http://docs.python.org/library/xml.sax.handler.html>} in order to process
    elements and create a L{Panel<UI.Panel.Panel>} with attached Widgets.
    For more information on how XML files are used with CAD-E, go I{here} (eventually - CAD).
    
    @type _basePath:       C{str}
    @ivar _basePath:       Base file path to be passed to UI elements for instantiation.
    
    @type _map:            L{GameMap<Map.GameMap.GameMap>}                   
    @ivar _map:            Map to be passed to UI elements for instantiation.
    
    @type _returnPanel:    C{list}
    @ivar _returnPanel:    List to populate with the B{single} outermost L{Panel<UI.Panel.Panel>}.
    
    @type _panels:         C{list}
    @ivar _panels:         Stack of L{Panel<UI.Panel.Panel>}s created from the XML document.
    """

    def __init__(self, basePath, map, panel):
        """
        Create a new U{C{ContentHandler}<http://docs.python.org/library/xml.sax.handler.html>} to process XML nodes.
        
        @type  basePath: C{str}
        @param basePath: Base file path to be passed to UI elements for instantiation.
        
        @type  map:      L{GameMap<Map.GameMap.GameMap>}
        @param map:      Map to be passed to UI elements for instantiation.
        
        @type  panel:    C{list}
        @param panel:    List to populate with the B{single} outermost L{Panel<UI.Panel.Panel>}.
        """
        self._basePath = basePath
        self._map = map
        self._returnPanel = panel
        
        self._panels = []
        
    def startElement(self, name, attrs):
        """
        Handles starting tags of new elements.  Instantiates UI elements and tracks the stack of
        L{Panel<UI.Panel.Panel>}s being created.
        
        @type  name:    C{unicode}
        @param name:    Name of the element.
        
        @type  attrs:   C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:   Attributes of the element.
        """
        # get the type and instantiate it
        if attrs.has_key('type'):
            type = attrs.get('type')
        else:
            if name == 'panel':
                type = 'UI.Panel'
            else:
                raise Exception('"' + name + '" not supported.  Try using the "type" attribute.')
        
        cls = ReflectionFunctions.GetPythonClass(type)
        instance = cls(*cls.AttributesToParameters(attrs, self._basePath, self._map))
        
        # add it to the last panel on the stack
        if self._panels:
            lastPanel = self._panels.pop()
            lastPanel.AddChild(instance)
            self._panels.append(lastPanel)
        
        if name == 'panel':
            if not self._panels:
                # first panel encountered, grab it to return
                self._returnPanel.append(instance)
                
            # new last panel on the stack
            self._panels.append(instance)
        
        if name == 'widget' and not self._panels:
            raise Exception('"widget" elements must be inside "panel" elements.')
    
    def endElement(self, name):
        """
        Handles ending tags of elements.  Removes the last L{Panel<UI.Panel.Panel>} from the stack
        of Panels being built.
        
        @type  name:    C{unicode}
        @param name:    Name of the element.
        """
        if name == 'panel':
            # pop off last panel
            self._panels.pop()
        