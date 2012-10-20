"""
A widget which displays a graphic from a file.

@author: Chris Alvarad-Dryden
"""

import UI
import pygame, os
from Core import Constants

class Textured(UI.Widget.Widget):
    """
    A widget which displays a graphic from a file.
    
    @type _rect:          U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar _rect:          The dimensions and position of the Widget in pixels.  The position is
                          relative to its parent's position.
    
    @type _parent:        L{Panel<UI.Panel.Panel>}
    @ivar _parent:        The Panel this Widget belongs to.
    
    @type _image:         U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _image:         Image to draw to the screen.
    
    @type _relPath:       C{str}
    @ivar _relPath:       File path to the image file, relative to the map file path this element is contained in. 
    
    @type Visible:        C{bool}
    @ivar Visible:        C{True} if the Widget should be drawn, C{False} otherwise.
    """
    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        Takes the values of the passed in dictionary then maps and arranges them into an appropriate
        parameter list for object construction.
        
        In addition to the normal L{Widget<UI.Widget.Widget>} attributes, it will also take C{'graphic'},
        which should be a relative (from the map it will be displayed on) file path to the image file.
        
        @type  attrs:     C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:     Attributes of the element.
        
        @type  basePath:  C{str}                                                       
        @param basePath:  Base file path to be used for resource loading.
        
        @type  map:       L{GameMap<Map.GameMap.GameMap>}
        @param map:       Used to reference objects within the map if the Widget needs to access them.
        
        @rtype:           C{list}
        @return:          Values of the attributes to be used as parameters, in parameter list order for the constructor.
        """
        params = UI.Widget.Widget.AttributesToParameters(attrs, basePath, map)
        
        path = attrs.get('graphic')
        path = os.path.normpath(os.path.realpath(os.path.join(basePath, path)))

        params.append(path)
        
        return params

    def __init__(self, position, width, height, absSurfPath):
        """
        Creates a new Textured UI widget at the position with the given dimensions and graphic.  If the graphic does
        not fit within the widget's bounds, it will be clipped.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  width:           C{int}
        @param width:           Width of the Widget.
        
        @type  height:          C{int}
        @param height:          Height of the Widget.
        
        @type  absSurfPath:     C{str}
        @param absSurfPath:     Absolute file path to the graphic.
        """
        UI.Widget.Widget.__init__(self, position, width, height)
        
        self._relPath = absSurfPath.lstrip(os.path.normpath(os.path.realpath(Constants.GameConstants.BASE_PATH)))
        path = os.path.normpath(os.path.realpath(absSurfPath))
        
        self._image = pygame.image.load(path)
        self._image.convert_alpha()

        
    def ToXMLString(self):
        """
        Generates XML to create this Widget.
        
        Ex:
        C{<widget type="UI.Textured" x="0" y="0" width="100" height="100" graphic="../content/gfx/element/timerHolder.png" />}
        
        @rtype:        C{unicode}
        @return:       XML string that can be read back through the XML parser.
        """
        xmlString = UI.Widget.Widget.__begin_typed_xml_string__(self)
        xmlString += 'graphic="' + self._relPath + '" '
        xmlString += '/>\n'
        
        return xmlString