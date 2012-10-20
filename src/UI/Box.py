"""
A simple colored rectangular UI element.
@author: Chris Alvarado-Dryden
"""

from UI.Widget import Widget
import pygame
import Utilities.HelperFunctions

class Box(Widget):
    """
    A simple colored rectangular UI element.
    
    @type _rect:          U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar _rect:          The dimensions and position of the Widget in pixels.  The position is
                          relative to its parent's position.
    
    @type _parent:        L{Panel<UI.Panel.Panel>}
    @ivar _parent:        The Panel this Widget belongs to.
    
    @type _image:         U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _image:         Image to draw to the screen.
    
    @type Visible:        C{bool}
    @ivar Visible:        C{True} if the Widget should be drawn, C{False} otherwise.
    
    @type _color:         U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _color:         The color of the Box.
    """
    
    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        Takes the values of the passed in dictionary then maps and arranges them into an appropriate
        parameter list for object construction.  It will not include a C{parent} parameter.
        
        In addition to the normal L{Widget<UI.Widget.Widget>} attributes, it will also take C{'color'}.
        
        @type  attrs:     C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:     Attributes of the element.  
        
        @type  basePath:  C{str}                                                       
        @param basePath:  Base file path to be used for resource loading.
        
        @type  map:       L{GameMap<Map.GameMap.GameMap>}
        @param map:       Used to reference objects within the map if the Widget needs to access them.
        
        @rtype:           C{list}
        @return:          Values of the attributes to be used as parameters, in parameter list order for the constructor.                                                           
        """
        params = Widget.AttributesToParameters(attrs, basePath, map)
        
        colorTup = attrs.get('color')
        colorTup = Utilities.HelperFunctions.StringConversions.StringToIntTuple(colorTup)
        color = pygame.Color(colorTup[0], colorTup[1], colorTup[2])
        if len(colorTup) > 3:
            color.a = colorTup[3]
        
        params.append(color)
        
        return params

    def __init__(self, position, width, height, color):
        """
        Creates a new Box UI widget at the position with the given dimensions and color.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  width:           C{int}
        @param width:           Width of the Widget.
        
        @type  height:          C{int}
        @param height:          Height of the Widget.
        
        @type  color:           U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
        @param color:           The color of the Box.
        """
        
        Widget.__init__(self, position, width, height)
        self._color = color
        
        self._image = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        self._image.convert_alpha()
        self._image.fill(self.Color)
        
    def ToXMLString(self):
        """
        Generates XML to create this Widget.
        
        Ex:
        C{<widget type="UI.Box" x="50" y="50" width="100" height="100" color="(0, 0, 255, 255)" />}
        
        @rtype:        C{unicode}
        @return:       XML that can be read back through the XML parser.
        """
        
        xmlString = Widget.__begin_typed_xml_string__(self)
        xmlString += 'color="' + self.Color.__str__() + '" '
        xmlString += '/>\n'
        
        return unicode(xmlString)
    
    ############### PROPERTIES ############### 
    def __get_color__(self):
        return self._color
    def __set_color__(self, value):
        self._color = value
        self._image.fill(self._color)
        
    Color = property(__get_color__, __set_color__, None, "The U{C{Color}<http://www.pygame.org/docs/ref/color.html>} of this Box.")