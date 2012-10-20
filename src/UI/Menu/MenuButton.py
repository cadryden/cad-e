"""
A button to be placed within a L{Menu<UI.Menu.Menu.Menu>}.

@author: Chris Alvarado-Dryden
"""

import UI
import Core.Constants

class MenuButton(UI.Widget.Widget):
    """
    A button to be placed within a L{Menu<UI.Menu.Menu.Menu>}.  A menu button can perform actions when it is
    highlighted, de-highlighted, and selected.  Navigation between menu buttons is established by setting the names
    of its neighbors to the names of other menu buttons on the same menu. 
    
    @type _menu:                    L{Menu<UI.Menu.Menu.Menu>}
    @ivar _menu:                    C{Menu} this button belongs to.
    
    @type Name:                     C{str}
    @ivar Name:                     Name of this button.
    
    @type AboveNeighborName:        C{str}
    @ivar AboveNeighborName:        Name of the C{MenuButton} above this one.
    
    @type BelowNeighborName:        C{str}
    @ivar BelowNeighborName:        Name of the C{MenuButton} below this one.
    
    @type LeftNeighborName:         C{str}
    @ivar LeftNeighborName:         Name of the C{MenuButton} to the left of this one.
    
    @type RightNeighborName:        C{str}
    @ivar RightNeighborName:        Name of the C{MenuButton} to the right of this one.
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
        params = UI.Widget.Widget.AttributesToParameters(attrs, basePath, map)
        
        params.append(attrs.get('name'))
        
        # menu
        params.append(None)
        
        neighbors = {}
        
        aboveName = Core.Constants.MenuCosntants.BUTTON_ABOVE
        belowName = Core.Constants.MenuCosntants.BUTTON_BELOW
        leftName = Core.Constants.MenuCosntants.BUTTON_LEFT
        rightName = Core.Constants.MenuCosntants.BUTTON_RIGHT

        if attrs.has_key('above'):
            neighbors[aboveName] = attrs.get(aboveName)
            
        if attrs.has_key('below'):
            neighbors[belowName] = attrs.get(belowName)
            
        if attrs.has_key('left'):
            neighbors[leftName] = attrs.get(leftName)
            
        if attrs.has_key('right'):
            neighbors[rightName] = attrs.get(rightName)
        
        params.append(neighbors)
        return params

    def __init__(self, position, width, height, name, menu=None, neighbors=None):
        """
        Creates a new Menu Button with the given relative position, width, height, and name, inside of the
        given Menu.  By default, it has no neighbors.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  width:           C{int}
        @param width:           Width of the Widget.
        
        @type  height:          C{int}
        @param height:          Height of the Widget.
        
        @type  name:            C{str}
        @param name:            Name of this MenuButton.
        
        @type  menu:            L{Menu<UI.Menu.Menu.Menu>}
        @param menu:            The Menu this MenuButton belongs to.
        
        @type  neighbors:       C{dict}
        @param neighbors:       Dictionary containing names (C{str}) of neighboring Menu Buttons.  Keys should be:
                                    - C{above}
                                    - C{below}
                                    - C{left}
                                    - C{right}
        """
        UI.Widget.Widget.__init__(self, position, width, height)
        
        # menu I belong to.  might not be parent
        self._menu = menu
        self.Name = name
        
        self.AboveNeighborName = ''
        self.BelowNeighborName = ''
        self.LeftNeighborName = ''
        self.RightNeighborName = ''
        
        aboveName = Core.Constants.MenuCosntants.BUTTON_ABOVE
        belowName = Core.Constants.MenuCosntants.BUTTON_BELOW
        leftName = Core.Constants.MenuCosntants.BUTTON_LEFT
        rightName = Core.Constants.MenuCosntants.BUTTON_RIGHT
        
        if neighbors:
            if neighbors.has_key(aboveName):
                self.AboveNeighborName = neighbors[aboveName]
            
            if neighbors.has_key(belowName):
                self.BelowNeighborName = neighbors[belowName]
                
            if neighbors.has_key(leftName):
                self.LeftNeighborName = neighbors[leftName]
                
            if neighbors.has_key(rightName):
                self.RightNeighborName = neighbors[rightName]
        
    def OnSelect(self):
        """
        B{[Stub]} Called when this button is selected.
        """
        return
    
    def OnHighlight(self):
        """
        B{[Stub]} Called when this button is highlighted, but not yet been selected.
        """
        return
    
    def OnDeHighlight(self):
        """
        B{[Stub]} Called when this button should no longer be highlighted.
        """
        return
    
    
    def ToXMLString(self):
        """
        Generates XML to create this Widget.

        Ex:
        C{<widget type="Example.PlatformerMenuButton" x="150" y="325" width="250" height="70" name="options" above="level select" target="Options" font="Arial" size="72" text="LEVEL SELECT" color="(220, 220, 220, 255)" />}

        @rtype:        C{unicode}
        @return:       XML that can be read back through the XML parser.
        """
        xmlString = UI.Widget.Widget.__begin_typed_xml_string__(self)
        xmlString += 'name="' + self.Name + '" '
        
        if self.AboveNeighborName:
            xmlString += 'above="' + self.AboveNeighborName + '" '
            
        if self.BelowNeighborName:
            xmlString += 'below="' + self.BelowNeighborName + '" '
            
        if self.LeftNeighborName:
            xmlString += 'left="' + self.LeftNeighborName + '" '
            
        if self.RightNeighborName:
            xmlString += 'right="' + self.RightNeighborName + '" '
        
        xmlString += '/>\n'
        return xmlString