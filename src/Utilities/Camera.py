'''
A viewport into the game world, which is displayed in the U{pygame<http://pygame.org/>} window.

@author: Chris Alvarado-Dryden
'''
import os
import pygame
from Core import Constants
import Utilities.HelperFunctions

from Core.Actor import Actor
from vector import Vector

from States.Camera.TargetState import TargetState
from States.Camera.StaticState import StaticState

from UI.Panel import Panel

class Camera(Actor):
    """
    A Camera is a viewport into the game world, which is displayed in the U{pygame<http://pygame.org/>} window.  In the game world,
    the Camera behaves as an L{Actor<Actor.Actor>}, and its bounding box is the view area.  Anything within its bounds will be
    rendered to the display view.
    
    The display view exists in screen space, defined by the window.  While it can take up the entire area of the window, it isn't
    necessary.  If the display view is smaller than the window, borders will automatically be drawn around it.  This to easily see
    the divide between displays when using multiple cameras.  If the display view and world view are not the same size, the world
    view will be scaled to match the display view dimensions.
    
    Additionally, Cameras can be used to handle UI elements through an internal L{Panel<UI.Panel.Panel>} that covers the display
    view.  All attached UI elements have their logic and drawing handled by the Camera. 

    @type windowSurf:     C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
    @cvar windowSurf:     Entire pygame window surface.  Each Camera will draw to this when L{Camera.FinalizeDraw} is called.
                          It is initialized in the L{Game constructor<Core.Game.Game.__init__>} as the full window size.
                          
    @type windowPanel:    L{Panel<UI.Panel.Panel>}
    @cvar windowPanel:    UI panel that covers the entire pygame window surface.  Every Camera's individual C{Panel} is a child to
                          this.
    
    @type _worldSurf:     C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
    @ivar _worldSurf:     World view surface.  Each Camera draws what it can see here at full resolution.
    
    @type _displaySurf:   C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
    @ivar _displaySurf:   Display view surface.  The scaled L{_worldSurf} which is drawn to the pygame window.
    
    @type _displayRect:   C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
    @ivar _displayRect:   The Camera's dimensions and position within the pyGame window.
    
    @type _borders:       C{list}
    @ivar _borders:       Four U{C{pygame.Rects}<http://www.pygame.org/docs/ref/rect.html>}, which divide the display views.
    
    @type _borderWidth:   C{int}
    @ivar _borderWidth:   Width of each border.
    
    @type _borderColor:   C{U{pygame.Color<http://www.pygame.org/docs/ref/color.html>}}
    @ivar _borderColor:   Color of the borders.
    
    @type _target:        L{GameObject} or C{(int, int)}
    @ivar _target:        Where the Camera is centered at all times.  If it is a GameObject it will use
                          L{GameObject.Center<GameObject.GameObject.Center>}.
    
    @type _order:         C{int}
    @ivar _order:         When using multiple Cameras, determines the order in which they should be displayed.
    
    @type _panel:         L{Panel<UI.Panel.Panel>}
    @ivar _panel:         A panel that covers the entirety of this Camera's display view.
    
    @type _uiPaths:       C{list}
    @ivar _uiPaths:       List of file paths (C{str}) relative to the location of the L{GameMap<Map.GameMap.GameMap>} .TMX
                          that the Camera resides in, which stores UI definitions for the Camera.
    """

    # static variable that represents the whole screen
    # set on the initialization of the Game object
    windowSurf = None
    windowPanel = None
    
    @staticmethod
    def Initialize(screenSurface):
        """
        Initializes the Camera system to the given screen size.
        
        @type  screenSurface:        C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @param screenSurface:        Surface which all Cameras will ultimately draw to.
        """
        Camera.windowSurf = screenSurface
        Camera.windowPanel = Panel((0, 0), screenSurface.get_width(), screenSurface.get_height())
    
    @staticmethod
    def StaticClear(color):
        """
        Fills the entire window with the given color.  This is usually used to wipe the screen
        before drawing anything else.
        
        @type  color:    C{U{pygame.Color<http://www.pygame.org/docs/ref/color.html>}}
        @param color:    The color to fill the screen with. 
        """
        sprite = pygame.Surface(Camera.windowSurf.get_size())
        sprite = sprite.convert_alpha()
        sprite.fill(color)
        
        Camera.windowSurf.blit(sprite, (0, 0))

    @staticmethod
    def PropertiesToParameters(properties):
        """
        Takes the values of the passed in dictionary and arranges them into an appropriate parameter list.
        In addition to the U{Tiled<http://mapeditor.org/>} Object Properties, the dictionary will also include position,
        width, and height.
        
        For Cameras, also reads the display view rectangle, target, camera order, and any UI files which will be overlaid
        on the display view.
        
        @type  properties:    C{dict}
        @param properties:    A dictionary of property names : values
        
        @rtype:               C{list}
        @return:              Values of the properties to be used as parameters, in parameter list order for the constructor.
        """
        params = []
        
        # world view
        worldView = pygame.Rect(properties['x'], properties['y'], properties['width'], properties['height'])
        
        # get the display view if it's there
        displayView = None
        if (properties.has_key(Constants.EditorConstants.OBJ_CAM_PROP_DISP_VIEW) and properties[Constants.EditorConstants.OBJ_CAM_PROP_DISP_VIEW].strip()):
            string  = properties[Constants.EditorConstants.OBJ_CAM_PROP_DISP_VIEW]
            tup = Utilities.HelperFunctions.StringConversions.StringToIntTuple(string)
            displayView = pygame.Rect(tup)
        
        # target
        target = None
        targetName = 'Camera Target'
        
        if (properties.has_key(Constants.EditorConstants.OBJ_CAM_PROP_TARGET) and properties[Constants.EditorConstants.OBJ_CAM_PROP_TARGET].strip()):
            string = properties[Constants.EditorConstants.OBJ_CAM_PROP_TARGET].strip()
            # coordinates
            if (string[0] == '('):
                target = Utilities.HelperFunctions.StringConversions.StringToIntTuple(string)
                targetName = 'Coordinate ' + target.__str__()
            # name
            else:
                target = None
                targetName = string
        else:
            target = worldView.center
            targetName = 'Coordinate ' + target.__str__()
        
        # order    
        order = 0
        if (properties.has_key(Constants.EditorConstants.OBJ_CAM_PROP_ORDER) and properties[Constants.EditorConstants.OBJ_CAM_PROP_ORDER].strip()):
            order = int(properties[Constants.EditorConstants.OBJ_CAM_PROP_ORDER].strip())
            
        # any UI files
        uiPaths = None
        if (properties.has_key(Constants.EditorConstants.OBJ_CAM_PROP_UI_FILE) and properties[Constants.EditorConstants.OBJ_CAM_PROP_UI_FILE].strip()):
            uiPaths = map(unicode.strip, properties[Constants.EditorConstants.OBJ_CAM_PROP_UI_FILE].split(','))
        
        params.append(worldView)
        params.append(displayView)
        params.append(properties['name'])
        params.append(target)
        params.append(targetName)
        params.append(order)
        params.append(uiPaths)
        
        return params

    def __init__(self, worldView, displayView=None, name=None, target=(0, 0), targetName=None, order=0, uiPaths=None):
        """
	    Creates a new Camera object, with the given viewing area and display area, and tracking the given target.
	    
	    If C{displayView == None}, the display will be the same dimensions as the world view rectangle,
	    but positioned at the top left corner of the window.
    
        @type  worldView:       C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param worldView:       Camera's area of view and position within the game world.
        
        @type  displayView:     C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param displayView:     Dimensions and position of the display inside the pygame window.

        @type  name:            C{str}
        @param name:            Name of this Camera.

        @type  target:          C{L{GameObject<GameObject.GameObject>} | (int, int)}
        @param target:          Where the Camera should always be centered.
        
        @type  targetName:      C{str}
        @param targetName:      Name of the object this Camera should be focused on.

        @type  order:           C{int}
        @param order:           When using multiple Cameras, determines the order in which they should be displayed.
        
        @type  uiPaths:         C{list}
        @param uiPaths:         List of file paths (C{str}) relative to the location of the
                                L{GameMap<Map.GameMap.GameMap>} .TMX that the Camera resides in.
        """
        targetStateName = Constants.StateConstants.CAM_TRACK_TARGET_NAME
        staticStateName = Constants.StateConstants.CAM_STATIC_NAME
        Actor.__init__(self, worldView.topleft, worldView.width, worldView.height, name, [], '', [(targetStateName, TargetState(self)), (staticStateName, StaticState(self))], targetStateName, None)
        # bounding box is world rect
        
        # default to a window screen with the same dimensions as the world view, placed at the top left of the window 
        if (displayView == None):
            displayView = pygame.Rect(worldView)
            displayView.topleft = (0, 0)
        
        self._displayRect = displayView
        
        # these will be set in the AdjustScreen calls
        self._worldSurf = None
        self._displaySurf = None
        self._panel = Panel((0, 0), 0, 0)
        Camera.windowPanel.AddChild(self._panel)
            
        self._order = order
        
        self._borders = []
        self._borderWidth = Constants.CameraConstants.BORDER_WIDTH
        self._borderColor = Constants.CameraConstants.BORDER_COLOR
        
        self._target = target
        self.targetName = targetName
        
        self.AdjustWorldView(worldView)
        self.AdjustDisplayView(displayView)
        
        
        if (isinstance(self.Target, tuple)):
            self.ChangeState(staticStateName)
            self.Center = self.Target
            
        self._uiPaths = uiPaths

    def LoadUIs(self):
        """
        Loads the UIs from the file paths given in the L{constructor<Camera.__init__>}.
        """
        if self._uiPaths:
            for uiPath in self._uiPaths:
                uiPath = os.path.normpath(os.path.join(os.path.dirname(self.Map.FilePath), uiPath))
                if os.path.isfile(uiPath):
                    self._panel.AddChild(Panel.PanelFromXML(uiPath, Constants.GameConstants.BASE_PATH, self.Map))
                else:
                    raise Exception('Path "' + uiPath + '" could not be found.')
                
    def UnloadUIs(self):
        """
        Removes all of the UI components on this Camera from the display view.
        """
        Camera.windowPanel.RemoveChild(self._panel)

    def AdjustWorldView(self, worldRect):
        """
        Changes the position and dimensions of the world view.
        
        @type  worldRect:   C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param worldRect:   The Camera's area of view and position within the game world.
        """
        self._worldSurf = pygame.Surface((worldRect.width, worldRect.height))
        self._worldSurf.convert_alpha()
        self.boundingBox = worldRect

    def AdjustDisplayView(self, displayRect):
        """
        Changes the position and dimensions of the display view within the window.  Also creates
        new borders after adjusting the dimensions, and resizes the Camera's L{Panel<UI.Panel.Panel>}.
        
        @type  displayRect:   C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param displayRect:   The dimensions and position of the display inside the window.
        """
        self._displaySurf = pygame.Surface((displayRect.width, displayRect.height))
        self._displaySurf.convert_alpha()
        self._displayRect = displayRect
        
        self._panel.Position = displayRect.topleft
        self._panel.Width = displayRect.width
        self._panel.Height = displayRect.height

        self._borders = []
        
        top = pygame.Surface((self._displayRect.width, self._borderWidth), pygame.SRCALPHA)
        top.convert_alpha()
        left = pygame.Surface((self._borderWidth, self._displayRect.height), pygame.SRCALPHA)
        left.convert_alpha()
        
        top.fill(self._borderColor)
        left.fill(self._borderColor)
        
        halfWidth = self._borderWidth / 2.0
        
        # create these borders in window space.
        # top
        self._borders.append((top, top.get_rect(topleft = (self._displayRect.left, self._displayRect.top - halfWidth))))
        # bottom
        self._borders.append((top, top.get_rect(topleft = (self._displayRect.left, self._displayRect.bottom - halfWidth))))
        # left
        self._borders.append((left, left.get_rect(topleft = (self._displayRect.left - halfWidth, self._displayRect.top))))
        # right
        self._borders.append((left, left.get_rect(topleft = (self._displayRect.right - halfWidth, self._displayRect.top))))

    def Update(self, dt):
        """
        Update logic for the Camera based on its current L{State<States.State.State>} and any attached UI elements.  This
        can be used to track targets and give the Camera some intelligence.
        
        @type  dt:    C{float}
        @param dt:    Time in seconds since the last frame refresh.
        """
        Actor.Update(self, dt)
        self._panel.Update(dt)
        
    def Draw(self, sprite, position):
        """
        Draws the sprite to the screen at the given world position if the Camera can see it.
        
	    @type  sprite:    C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
	    @param sprite:    The image which should be drawn to the screen.

	    @type  position:  C{(int, int)}
	    @param position:  The world coordinate where the top left of the sprite should be drawn.
	    """
        # check if this sprite is actually viewable on screen
        spriteRect = sprite.get_rect()
        spriteRect.topleft = position
        
        if (self.boundingBox.colliderect(spriteRect)):    
            # draw it if it is
            left = position[0] - self.Position[0]
            top = position[1] - self.Position[1]
            self._worldSurf.blit(sprite, (left, top))
            
    def DrawBorders(self):
        """
        Draws this Camera's borders if they're viewable.
        """
        for border, rect in self._borders: 
            centerX, centerY = rect.center
            if ((centerY > 0 and centerY < Camera.windowSurf.get_height()) and (centerX > 0 and centerX < Camera.windowSurf.get_width())):
                Camera.windowSurf.blit(border, rect.topleft)
        
    def Clear(self, color):
        """
        Fills the entire display view with the given color.  This is usually used to wipe the screen
        before drawing anything else.
        
        @type  color:    C{U{pygame.Color<http://www.pygame.org/docs/ref/color.html>}}
        @param color:    The color to fill the screen with.
        """
        sprite = pygame.Surface(self._worldSurf.get_size())
        sprite = sprite.convert_alpha()
        sprite.fill(color)
        
        self._worldSurf.blit(sprite, (0, 0))
    
    def FinalizeDraw(self):
        """
        Draws everything from this Camera to the L{pygame window<Camera.windowSurf>}.  If the the world
        view and display view are different sizes, the world view will be scaled to match the display.
        
        After the world view is drawn, all attached UI elements are drawn.
        """
        # scale everything from the 'at-resolution' world screen to the windowSurf display.
        pygame.transform.smoothscale(self._worldSurf, (self._displaySurf.get_width(), self._displaySurf.get_height()), self._displaySurf)

        Camera.windowSurf.blit(self._displaySurf, self._displayRect.topleft)
        
        # draw this camera's widgets to the full screen
        self._panel.DrawTo(Camera.windowSurf)
        
        
    def AddWidget(self, widget):
        """
        Adds a widget to this Camera's L{Panel<UI.Panel.Panel>}.
        
        @type  widget:        L{Widget<UI.Widget.Widget>}
        @param widget:        The widget to add.
        """
        self._panel.AddChild(widget)
        
    ############### PROPERTIES ###############        
    
    def __get_target__(self):
        return self._target
    
    def __set_target__(self, value):
        if (isinstance(value, Vector)):
            self._target = (value.x, value.y)
        else:
            self._target = value          
    
    def __get_order__(self):
        return self._order
    def __set_order__(self, value):
        self._order = value
    
    Target = property(__get_target__, __set_target__, None, "The Camera's target.  Either a L{GameObject<GameObject.GameObject>} or world coordinate.")
    Order = property(__get_order__, __set_order__, None, "The Camera's order relative to other Cameras.")