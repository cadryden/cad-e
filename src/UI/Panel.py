'''
An organizational structure used to hold L{Widget<UI.Widget.Widget>}s.

@author: Chris Alvarado-Dryden
'''

import os

from UI.Widget import Widget

class Panel(Widget):
    """
    An organizational structure used to hold L{Widget<UI.Widget.Widget>}s.  Panels 
    do not have have any logic or graphics, but they will clip any child widgets.
    
    @type _rect:          U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar _rect:          The dimensions and position of the Widget in pixels.  The position
                          is relative to its parent's position.
    
    @type _parent:        L{Panel<UI.Panel.Panel>}
    @ivar _parent:        The Panel this Widget belongs to.
    
    @type Visible:        C{bool}
    @ivar Visible:        C{True} if the Widget should be drawn, C{False} otherwise.
    
    @type _children:      C{list}
    @ivar _children:      List of L{Widget<UI.Widget.Widget>}s that belong to this Panel.
    """

    def __init__(self, position, width, height):
        """
        Creates a new Panel with no children at the given position relative to its parent,
        and with the given width and height.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  width:           C{int}
        @param width:           Width of the Widget.
        
        @type  height:          C{int}
        @param height:          Height of the Widget.
        """
        Widget.__init__(self, position, width, height)
        self._children = []
    
    @staticmethod
    def PanelFromXML(path, basePath, map):
        """
        Constructs a Panel from the .XML file at the given path, using the given
        L{GameMap<Map.GameMap.GameMap>} as a reference.
        
        For an explanation of the Panel's XML format, check here. [I'll link to something
        eventually - CAD]
        
        @type  path:        C{str}
        @param path:        Path to the .XML file containing the Panel definition.
        
        @type  basePath:    C{str}
        @param basePath:    Base file path the Panel and Widgets can use to to load resources.
        
        @type  map:         L{GameMap<Map.GameMap.GameMap>}
        @param map:         Map this Panel will use to access data if necessary.
        
        @rtype:             C{Panel}
        @return:            New Panel described by the given XML.
        """
        from UI.UIXMLLoader import UIXMLLoader
        import xml.sax

        panel = []

        handler = UIXMLLoader(basePath, map, panel)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(os.path.normpath(os.path.realpath(path)))
                
        return panel[0]
        
    def AddChild(self, child):
        """
        Adds the given Widget to this Panel.
        
        @type  child:        L{Widget<UI.Widget.Widget>}
        @param child:        The child to add to this Panel.
        """
        self._children.append(child)
        child._parent = self
        
        # special casing to add menu buttons to nearest menus
        from UI.Menu.MenuButton import MenuButton
        if isinstance(child, MenuButton):
            nearestMenu = self.__get_nearest_menu__() 
            if nearestMenu:
                child._menu = nearestMenu

    def RemoveChild(self, child):
        """
        Removes the given Widget from this Panel.
        
        @type  child:        L{Widget<UI.Widget.Widget>}
        @param child:        The child to remove from this Panel.
        """
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def Update(self, dt):
        """
        Runs any update logic this Panel and any children need.
        
        @type  dt:        C{float}
        @param dt:        Time since the last game frame was rendered.
        """
        for child in self._children:
            child.Update(dt)
    
    def IsParentOf(self, child):
        """
        Returns C{True} if this Panel is the parent of the Widget at any level of the family tree.
        
        @type  child:     L{UI.Widget.Widget<Widget>}
        @param child:     Potential child of this Panel.
        
        @rtype:           C{bool}
        @return:          C{True} if it is a parent (or grand parent, etc.) of the given child, C{False} otherwise.
        """
        return child.IsChildOf(self)
        
    def DrawTo(self, surf):
        """
        Draws this Panel's children to the given Surface if its visible.
        
        @type  surf:        C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @param surf:        Surface to draw to.
        """
        if not self.Visible:
            return
        
        for child in self._children:
            child.DrawTo(surf)
            
            
    def __get_nearest_menu__(self):
        """
        Looks up the family tree and returns the nearest Menu, starting with itself.
        
        @rtype:        L{Menu<UI.Menu.Menu.Menu>}
        @return:       Menu that is the closest parent to this Panel, or C{None} if there
                       are no Menus.
        """
        from UI.Menu.Menu import Menu
        
        if isinstance(self, Menu):
            return self
        elif self._parent == None:
            return None
        else:
            return self._parent.__get_nearest_menu__()
    
    def ToXMLString(self):
        """
        Generates XML to create this Panel and its children.
        
        @rtype:    C{unicode}
        @return:   XML formatted output. 
        """
        xmlString = '<panel '
        xmlString += 'x="'+ self.Position[0].__str__() +'" '
        xmlString += 'y="'+ self.Position[1].__str__() +'" '
        xmlString += 'width="'+ self._rect.width.__str__() +'" '
        xmlString += 'height="'+ self._rect.height.__str__() +'" '
        xmlString += '>\n'
        for child in self._children:
            xmlString += child.ToXMLString()
        xmlString += '</panel>\n' 
        
        return unicode(xmlString)
    
    def __begin_typed_xml_string__(self):
        """
        Creates the opening C{panel} tag with attributes: C{type, x, y, width, height}.
        
        @rtype:        C{unicode}
        @return:       Beginning of a panel tag that will have a C{type} attribute.
        """
        typeName = self.__class__.__module__
        
        xmlString = '<panel type="' + typeName + '" '
        xmlString += 'x="'+ self.Position[0].__str__() +'" '
        xmlString += 'y="'+ self.Position[1].__str__() +'" '
        xmlString += 'width="'+ self._rect.width.__str__() +'" '
        xmlString += 'height="'+ self._rect.height.__str__() +'" '
        
        return unicode(xmlString)