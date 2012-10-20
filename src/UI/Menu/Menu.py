"""
A menu used outside of game play to configure options, choose game modes, etc.

@author: Chris Alvarado-Dryden
"""

import UI
from Core import Constants

from UI.Menu.MenuButton import MenuButton

class Menu(UI.Panel.Panel):
    """
    A menu used outside of game play to configure options, choose game modes, etc.  Its two main components
    are the L{Controller<Utilities.Controller.Controller.Controller>}s, used for input processing, and a collection of
    L{MenuButton<UI.Menu.MenuButton.MenuButton>}s to control navigation between menus and the with the game.
    
    @type _buttons:            C{dict}
    @ivar _buttons:            A dictionary of L{MenuButton<UI.Menu.MenuButton.MenuButton>}s keyed on their names.
    
    @type _firstButton:        L{MenuButton<UI.Menu.MenuButton.MenuButton>}
    @ivar _firstButton:        The button to default to when entering a menu.
    
    @type _currentButton:      L{MenuButton<UI.Menu.MenuButton.MenuButton>}
    @ivar _currentButton:      The button that is currently highlighted.
    
    @type _prevMenu:           C{Menu}
    @ivar _prevMenu:           Menu that was before this one.  Defaults to itself.
    
    @type Game:                L{Game<Game.Game>}
    @cvar Game:                The Game all Menus belongs to.
    
    @type Name:                C{str}
    @ivar Name:                The name of this Menu.
    
    @type _controllers:        C{list}
    @ivar _controllers:        List of L{Controller<Utilities.Controller.Controller.Controller>}s to process
                               for input.
                               
    @type Controllable:        C{bool}
    @ivar Controllable:        C{True} if the menu can be controlled currently, C{False} otherwise.
    """

    # set in Game when Menus are being loaded
    Game = None
    
    
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
        
        params = []
        
        params.append(attrs.get('name'))
        
        x = 0
        y = 0
        if attrs.has_key('x'):
            x = int(attrs.get('x'))
        if attrs.has_key('y'):
            y = int(attrs.get('y'))
        params.append((x,y))
        
        if attrs.has_key('width'):
            params.append(int(attrs.get('width')))
        
        if attrs.has_key('height'):
            params.append(int(attrs.get('height')))
        
        return params

    def __init__(self, name, position=None, width=None, height=None):
        """
        Creates a new full screen sized Menu with the given name, and belonging to the given L{Game<Game.Game>}.
        The Menu position and size can be overridden using the C{position}, C{width} and C{height} parameters.
        
        @type  name:           C{str}
        @param name:           Name of the C{Menu}.
        
        @type  position:       C{(int, int)}
        @param position:       Override position of the Menu in pixels, relative to its parent.
        
        @type  width:          C{int}
        @param width:          Override width.
        
        @type  height:         C{int}
        @param height:         Override height.
        """

        if not position:
            position = (0, 0)

        if not width:
            width = Constants.GameConstants.WINDOW_WIDTH    
        if not height:
            height = Constants.GameConstants.WINDOW_HEIGHT
        
        UI.Panel.Panel.__init__(self, position, width, height)
        
        self._controllers = []
        self.Controllable = False
        self._buttons = {}
        self._firstButton = None
        self._currentButton = None
        
        self._prevMenu = self
        
        self.Name = name
        
    def AddChild(self, child):
        """
        Adds the given Widget to this Menu.  Handles L{MenuButton<UI.Menu.MenuButton.MenuButton>}s appropriately.
        
        @type  child:        L{Widget<UI.Widget.Widget>}
        @param child:        The child to add to this Menu.
        """
        UI.Panel.Panel.AddChild(self, child)
        
        if isinstance(child, MenuButton):
            if self._firstButton == None:
                self._firstButton = child
                self._currentButton = child
            self._buttons[child.Name] = child
        elif isinstance(child, Menu):
            self.Game.AddMenu(child)
    
    def Update(self, dt):
        """
        Handles input and runs any update logic this Menu and any children need.
        
        @type  dt:        C{float}
        @param dt:        Time since the last game frame was rendered.
        """
        if self.Controllable:
            self.ProcessInput()

        UI.Panel.Panel.Update(self, dt)  
                
    def ProcessInput(self):
        """
        B{[Stub]} Processes the input from the L{Controllers}.  Called from within L{Update}.
        """
        return
                       
    def OnExit(self):
        """
        Resets the menu to its original state.  Currently de-highlights the last button.
        """
        # clean up so when we come back here the  menu is the same
        self._currentButton.OnDeHighlight()
        
    def OnEnter(self):
        """
        Sets up the menu for when it will be entered.  Currently highlights its current
        button.
        """
        self._currentButton.OnDeHighlight()
        
        # reset to first button
        self._currentButton = self._firstButton
        self._currentButton.OnHighlight()
        
    def SwitchControlTo(self, menuName):
        """
        Disables control on this menu and enables it on the menu with the given name.  Also
        updates the history on the new menu.

        @type  menuName:        C{str}
        @param menuName:        Name of the menu to switch control to.
        """
        self.Controllable = False
        
        if menuName != None:
            menu = self.Game.GetMenu(menuName)
            menu.Controllable = True
            menu._currentButton.OnHighlight()
            
            # update history
            # if not going backwards
            if menu not in self.__family_previous_menus__():
                menu._prevMenu = self
    
    def __family_previous_menus__(self):
        """
        Returns a list of each menu's previous menu, starting with this menu and working
        up through its parents. 
        
        @rtype:        C{list}
        @return:       The previous menu for this menu and each parent.
        """
        prevMenus = []
        parent = self
        
        while parent != None:
            if isinstance(parent, Menu):
                prevMenus.append(parent._prevMenu)
            parent = parent._parent
            
        return prevMenus
        
    
    def OldestParentMenu(self):
        """
        Returns the highest menu in this menu's hierarchy of parents.
        
        @rtype:        C{Menu}
        @return:       The menu in this family tree which has no menus above it.
        """
        oldest = self
        parent = self._parent
        
        while parent != None:
            if isinstance(parent, Menu):
                oldest = parent
            parent = parent._parent
            
        return oldest
    
    def GetButton(self, name):
        """
        Gets the MenuButton from this Menu with the given name.
        
        @type  name:        C{str}
        @param name:        The name of the  L{MenuButton<UI.Menu.MenuButton.MenuButton>} to retrieve from this Menu.
        
        @rtype:             L{MenuButton<UI.Menu.MenuButton.MenuButton>}
        @return:            The named child in this Menu, C{None} if it does not exist.
        """
        if self._buttons.has_key(name):
            return self._buttons[name]
        else:
            return None
    
    def ToXMLString(self):
        """
        Generates XML to create this Menu, including all of its children.
        
        Ex:
        C{<panel type="Example.PlatformerMenu" x="0" y="0" width="800" height="600" name="Main Menu" >}
        
        @rtype:        C{unicode}
        @return:       XML that can be read back through the XML parser.
        """
        xmlString = UI.Panel.Panel.__begin_typed_xml_string__(self)
        xmlString += 'name="' + self.Name + '" '
        
        xmlString += '>\n'
        
        # Menu specific stuff
        for child in self._children:
            xmlString += child.ToXMLString()
        
        xmlString += '</panel>'
        return unicode(xmlString)
    
    def __str__(self):
        """
        Name of the menu.
        
        @rtype:     C{str}
        @return:    String representation of the Menu.
        """
        return self.Name
    
    ############### PROPERTIES ###############
    
    def __get_controllers__(self):
        return self._controllers
        
    def __set_controllers__(self, value):
        self._controllers = value
        
        for child in self._children:
            if isinstance(child, Menu):
                child.Controllers = value
                
    Controllers = property(__get_controllers__, __set_controllers__, None, "List of L{Controller<Utilities.Controller.Controller.Controller>}s to process for input.")