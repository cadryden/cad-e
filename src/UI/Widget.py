'''
B{[Base Class]} A single UI element, the foundation of UI screens and menus.

@author: Chris Alvarado-Dryden
'''

import pygame

from Utilities.vector import Vector

class Widget(object):
    """
    B{[Base Class]} A single UI element, the foundation of interface screens and menus.  All UI elements
    derive from Widget, and have a position, width, and height measured in pixels.  The
    position is relative to its parent's position, and if its area is not completely enclosed by its
    parent, the widget will be clipped.
    
    @type _rect:          U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar _rect:          The dimensions and position of the Widget in pixels.  The position is
                          relative to its parent's position.
    
    @type _parent:        L{Panel<UI.Panel.Panel>}
    @ivar _parent:        The Panel this Widget belongs to.
    
    @type _image:         U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _image:         Image to draw to the screen.
    
    @type Visible:        C{bool}
    @ivar Visible:        C{True} if the Widget should be drawn, C{False} otherwise.
    """

    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        Takes the values of the passed in dictionary then maps and arranges them into an appropriate
        parameter list for object construction.  This is used primarily when loading UI elements from
        an XML file.
        
        @type  attrs:     C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:     Attributes of the element.         
        
        @type  basePath:  C{str}                                                       
        @param basePath:  Base file path to be used for resource loading.
        
        @type  map:       L{GameMap<Map.GameMap.GameMap>}
        @param map:       Used to reference objects within the map if the Widget needs to access them.
        
        @rtype:           C{list}
        @return:          Values of the attributes to be used as parameters, in parameter list order for the constructor.
        """
        params = []
        
        params.append((int(attrs.get('x')), int(attrs.get('y'))))
        params.append(int(attrs.get('width')))
        params.append(int(attrs.get('height')))
        
        return params

    def __init__(self, position, width, height):
        """
        Creates a new Widget, with the given relative position (to whatever parent it may have), width and
        height.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  width:           C{int}
        @param width:           Width of the Widget in pixels.
        
        @type  height:          C{int}
        @param height:          Height of the Widget in pixels.
        """
        
        self._parent = None
        self._rect = pygame.Rect(position[0], position[1], width, height)
        self._image = None
        self.Visible = True
        
    def Update(self, dt):
        """
        B{[Stub]} Runs any update logic this Widget needs.
        
        @type  dt:        C{float}
        @param dt:        Time since the last game frame was rendered.
        """
        return
        
    def CenterToParent(self):
        """
        Centers the Widget to its parent. 
        """
        if self._parent:
            parentRect = self._parent._rect.copy()
            parentRect.topleft = (0, 0)
            self._rect.center = parentRect.center
    
    def IsChildOf(self, parent):
        """
        Returns C{True} if this Widget is the child of the panel at any level of the family tree.
        
        @type  parent:    L{Panel<UI.Panel.Panel>}
        @param parent:    Potential parent to this Widget.
        
        @rtype:           C{bool}
        @return:          C{True} if it is a child (or grand child, etc.) of the given parent, C{False} otherwise.
        """
        if self._parent == None:
            return False
        elif self._parent == parent:
            return True
        else:
            return self._parent.IsChildOf(parent)
        
    def DrawTo(self, surf):
        """
        Draws this Widget to the given Surface if its visible.  If the Widget is not completely within
        its parent's panel, it will be clipped.
        
        @type  surf:        C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @param surf:        Surface to draw this Widget to.
        """
        
        if not self._image or not self.Visible:
            return
        
        area = self.__drawable_area__()
        if area.width > 0 and area.height > 0:
            area.topleft = (0, 0)
            surf.blit(self._image, self.AbsolutePosition, area)
    
    def __drawable_area__(self):
        """
        Returns a new rectangle which represents the area this Widget may draw to.
        The area will be clipped from its parent's area.
        
        @rtype:        C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}  
        @return:       Area that can be drawn to.
        """
        if not self._parent:
            return self._rect.copy()
        
        parentArea = self._parent.__drawable_area__()
        parentArea.topleft = (0, 0)
        area = self._rect.clip(parentArea)
        
        return area
            
    def __begin_typed_xml_string__(self):
        """
        Creates the opening C{widget} tag with attributes: C{type, x, y, width, height}.
        
        @rtype:        C{unicode}
        @return:       Opening XML tag with common Widget attributes.
        """
        typeName = self.__class__.__module__
        
        xmlString = '<widget type="' + typeName + '" '
        xmlString += 'x="'+ self.Position[0].__str__() +'" '
        xmlString += 'y="'+ self.Position[1].__str__() +'" '
        xmlString += 'width="'+ self._rect.width.__str__() +'" '
        xmlString += 'height="'+ self._rect.height.__str__() +'" '
        
        return unicode(xmlString)
    
    ############### PROPERTIES ###############
    
    def __get_position__(self):
        return self._rect.topleft
    
    def __set_position__(self, value):
        self._rect.left = value[0]
        self._rect.top = value[1]
        
    def __get_abs_position__(self):
        if self._parent == None:
            return self.Position
        else:
            return Vector(self._parent.AbsolutePosition) + Vector(self.Position)
        
    def __get_width__(self):
        return self._rect.width
    def __set_width__(self, value):
        self._rect.width = value
        
    def __get_height__(self):
        return self._rect.height
    def __set_height__(self, value):
        self._rect.height = value
        
    Position = property(__get_position__, __set_position__, None, "Coordinate of the top left corner of the Widget relative to its parent.")
    AbsolutePosition = property(__get_abs_position__, None, None, "Absolute coordinate of the top left corner of the Widget.")
    Width = property(__get_width__, __set_width__, None, "The width of the Widget in pixels.")
    Height = property(__get_height__, __set_height__, None, "The height of the Widget in pixels.")