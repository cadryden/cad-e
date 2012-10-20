'''
The Game class controls the flow of the game and interfaces with the outside world (input and output).

@author: Chris Alvarado-Dryden
'''

from Core.Sound import Sound
from Core.MusicPlayer import MusicPlayer
import os
import gc
import pygame
from pygame.locals import *

from Core import Constants

from Map.GameMap import GameMap
from Utilities.Camera import Camera

from Utilities.Controller.Controller import Controller

from UI.Panel import Panel
from UI.Menu.Menu import Menu

class Game(object):
    """
    The Game class controls the flow of the game and interfaces with the outside world (input and output),
    and the transitions between game play and menus.
    
    @type _clock:              U{C{pygame.time.Clock}<http://www.pygame.org/docs/ref/time.html#pygame.time.Clock>}
    @ivar _clock:              Used to keep track of the time between frames.
                              
    @type _maxFPS:             C{int}
    @ivar _maxFPS:             Upper bound on the FPS.
                              
    @type _controllers:        C{list}
    @ivar _controllers:        All L{Controller<Utilities.Controller.Controller.Controller>}s that can receive input.
                              
    @type _map:                L{GameMap<Map.GameMap.GameMap>}
    @ivar _map:                The current map being played.
                              
    @type _mapPathList:        C{list}
    @ivar _mapPathList:        List of all L{GameMap<Map.GameMap.GameMap>} file paths in the game.  In order of when
                               they were loaded. 
                              
    @type _mapPathDict:        C{dict}
    @ivar _mapPathDict:        C{{str : str}} -  All L{GameMap<Map.GameMap.GameMap>} file paths in the game keyed by their
                               L{FileName<Map.GameMap.GameMap.FileName>}.
                                                             
    @type _displayMenu:        L{Menu<UI.Menu.Menu.Menu>}
    @ivar _displayMenu:        Menu that is currently being displayed.  It should not be a sub-menu.
                              
    @type _controlMenu:        L{Menu<UI.Menu.Menu.Menu>}
    @ivar _controlMenu:        Menu that is currently processing input.  It may be a sub-menu or the same as the display menu.
                               
    @type _menuDict:           C{dict}
    @ivar _menuDict:           C{{str : L{Menu<UI.Menu.Menu.Menu>}}} - All Menus in the game, keyed by their
                               L{Name<UI.Menu.Menu.Menu.Name>}.
                          
    @type _nextDisplayMenu:    L{Menu<UI.Menu.Menu.Menu>}
    @ivar _nextDisplayMenu:    Will become the display menu at the beginning of the next frame.
    
    @type _nextControlMenu:    L{Menu<UI.Menu.Menu.Menu>}
    @ivar _nextControlMenu:    Will become the control menu at the beginning of the next frame.
    """

    def __init__(self, title='cadGame', iconPath=None, windowWidth=640, windowHeight=480, maxFPS=60, soundFreq=44100, soundBits=16, soundChannels=8, stereo=True, openGLMode=False):
        """
        Creates a Game with the given title, icon, screen dimensions, maximum FPS, and sound attributes.
        The game will be empty of any objects, but the screen, sound system, and controllers will be initialized.
        
        @type  title:            C{str}
        @param title:            Title for the U{pygame display<http://www.pygame.org/docs/ref/display.html>}.
        
        @type  iconPath:         C{str}
        @param iconPath:         File path to an image file to be used as an icon for the
                                 U{pygame display<http://www.pygame.org/docs/ref/display.html>}.
        
        @type  windowWidth:      C{int}
        @param windowWidth:      Width of the pygame display in pixels.
        
        @type  windowHeight:     C{int}
        @param windowHeight:     Height of the pygame display in pixels.
        
        @type  maxFPS:           C{int} 
        @param maxFPS:           Maximum frames per second the game will run at.  The game may run slower
                                 than this value.
                         
        @type  soundFreq:        C{int}
        @param soundFreq:        Sample rate for all sounds and music, in hertz.
        
        @type  soundBits:        C{int}
        @param soundBits:        Bits used per sound sample.
        
        @type  soundChannels:    C{int}
        @param soundChannels:    The number of channels available to play sound on simultaneously.
        
        @type  stereo:           C{bool}
        @param stereo:           C{True} if stereo, C{False} if mono.
        
        @type  openGLMode:       C{bool}
        @param openGLMode:       C{True} if using OpenGL, C{False} if software.
        """
        
        # initialize pygame
        print 'Initializing pygame'
        
        if iconPath:
            icon = pygame.image.load(os.path.normpath(os.path.realpath(iconPath)))
            pygame.display.set_icon(icon)
            pygame.display.set_caption(title)
        
        if openGLMode:
            from OpenGL.GL import *
            from OpenGL.GLU import *
            screen = pygame.display.set_mode((windowWidth, windowHeight), pygame.OPENGL|pygame.DOUBLEBUF, 0)
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, windowWidth, 0, windowHeight)
            glMatrixMode(GL_MODELVIEW)
            
            #set up texturing
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        else:
            screen = pygame.display.set_mode((windowWidth, windowHeight), 0, 0)
            screen.convert_alpha()
            
        pygame.init()
        
        # sound
        Sound.Initialize(soundFreq, soundBits, stereo, soundChannels)
        
        musicPlayer = MusicPlayer()
        musicPlayer.Volume = Constants.GameConstants.MUSIC_VOLUME
        
        # so Cameras can draw to the screen and UIs work
        Camera.Initialize(screen)
        
        # to get our fps
        self._clock = pygame.time.Clock()
        self._maxFPS = maxFPS
        
        # the current map
        self._map = None
        
        self._mapPathList = []
        self._mapPathDict = {}
        
        # menus
        self._menuDict = {}
        self._displayMenu = None
        self._controlMenu = None
        self._nextDisplayMenu = None
        self._nextControlMenu = None
        
        Menu.Game = self
        
        # controllers
        self._controllers = []
        self.__initialize_controllers__(Constants.ControllerConstants.CONTROLLERS_XML_PATH)
        
    def __initialize_controllers__(self, path):
        """
        Creates default L{Controller<Utilities.Controller.Controller.Controller>}s for the game and binds
        them to hardware input.
        
        @type  path:        C{str}
        @param path:        File path to the .XML file where the Controllers are defined. 
        """ 
        for controller in Controller.ControllerFromXML(os.path.normpath(os.path.realpath(path))):
            self._controllers.append(controller)
        
    def LoadMaps(self, paths):
        """
        Loads each L{GameMap<Map.GameMap.GameMap>} from the given paths and inserts them into the map structures.
        
        @type  paths:   C{list}
        @param paths:   List of relative file paths to the .TMX files.
        """
        for path in paths:
            self.LoadMap(path)

    def LoadMap(self, path):
        """
        Loads some data for the L{GameMap<Map.GameMap.GameMap>} at the given path into internal map structures.
        
        @type  path:    C{str}
        @param path:    Relative file path to the .TMX file.
        """
        path = os.path.normpath(os.path.realpath(path))
        fileName = os.path.basename(path)
        
        if self._mapPathDict.has_key(fileName):
            raise Exception('Map "' + fileName + '" already loaded.')
        else:
            self._mapPathList.append(path)
            self._mapPathDict[fileName] = path      
    
    def PlayMap(self, m, transferFromLastMap=False):
        """
        Sets the L{GameMap<Map.GameMap.GameMap>} with the given filename or index to be played.  If C{transferFromLastMap} is
        set, then the current GameMap will be used to transfer data into the new map for the marked objects.
        
        @type  m:                      C{str | int}
        @param m:                      Either a L{GameMap<Map.GameMap.GameMap>} name (C{'example.tmx'}) or index.
        
        @type  transferFromLastMap:    C{bool}
        @param transferFromLastMap:    C{True} if the previous map should be used to transfer object data from, C{False} otherwise.
        """

        # stop sounds
        if self.CurrentMap:
            self.CurrentMap.StopSounds()
            self.CurrentMap.RemoveUI()

        if isinstance(m, int):
            newMapPath = self.__map_path_by_index__(m)
        elif isinstance(m, str):
            newMapPath = self.__map_path_by_name__(m)
        else:
            raise Exception('Map "' + m + '" not found.  Check that it is being loaded first.')
        
        if (transferFromLastMap):
            transferMap = self.CurrentMap
        else:
            transferMap = None
                    
        newMap = GameMap(newMapPath, self.Controllers, transferMap)
        
        if newMap.MusicLoaded:
            MusicPlayer().Play()
            
        self._map = newMap
        
        # did some dirty things to restart, so try to clean it up
        gc.collect()
        
    def PlayNextMap(self, transferFromLastMap=False):
        """
        Plays the next L{GameMap<Map.GameMap.GameMap>} in the order they were loaded.
        
        @type  transferFromLastMap:    C{bool}
        @param transferFromLastMap:    C{True} if the previous map should be used to transfer object data from, C{False} otherwise.
        """
        if self.CurrentMap:
            currentIndex = self._mapPathList.index(self.CurrentMap.FilePath)
            nextIndex = (currentIndex + 1) % len(self._mapPathList)
        else:
            nextIndex = 0
        self.PlayMap(nextIndex, transferFromLastMap)
        
    def LoadMenu(self, path, controllers):
        """
        Loads the L{Menu<UI.Menu.Menu.Menu>} from the given path and inserts it into the menu structure.

        @type  path:           C{str}
        @param path:           Relative file path to the menu .XML file.
        
        @type  controllers:    C{list}
        @param controllers:    A list of L{Controller<Utilities.Controller.Controller.Controller>}s that can control 
                               this menu.
        """
        menu = Panel.PanelFromXML(path, Constants.GameConstants.BASE_PATH, None)
        
        if self._menuDict.has_key(menu.Name):
            raise Exception('Menu "' + menu.__str__() + '" already loaded.')
        else:
            self.AddMenu(menu)
            menu.Controllers = controllers
            
    def LoadMenus(self, paths, controllers):
        """
        Loads the L{Menu<UI.Menu.Menu.Menu>}s from the given list of paths and inserts them into the
        menu structure.

        @type  paths:           C{list}
        @param paths:           List of relative file paths to the menu .XML files.
        
        @type  controllers:    C{list}
        @param controllers:    A list of L{Controller<Utilities.Controller.Controller.Controller>}s that can control 
                               these menus.
        """
        for path in paths:
            self.LoadMenu(path, controllers)
            
    def LoadMenusFrom(self, dir, controllers):
        """
        Load all L{Menu<UI.Menu.Menu.Menu>}s found in the given directory.
        
        @type  dir:            C{str}
        @param dir:            Relative path from L{GameConstants.BASE_PATH<Utilities.Constants.GameConstants.BASE_PATH>}
                               to the directory containing the menu definitions. 
        
        @type  controllers:    C{list}
        @param controllers:    A list of L{Controller<Utilities.Controller.Controller.Controller>}s that can control 
                               these menus.
        """
        menuDirectory = os.path.join(Constants.GameConstants.BASE_PATH, dir)
        menuDirectory = os.path.realpath(os.path.normpath(menuDirectory))
        for root, dirs, files in os.walk(menuDirectory):
            for file in files:
                if file[-4:].lower() == '.xml':
                    self.LoadMenu(os.path.join(root, file), controllers)
            break
        
        
    def AddMenu(self, menu):
        """
        Adds the given menu to the game's menu structure. 
        
        @type  menu:        L{Menu<UI.Menu.Menu.Menu>}
        @param menu:        Menu to add to the game.
        """
        self._menuDict[menu.Name] = menu
        
    def TransitionToMenu(self, m):
        """
        Set up the transition between the current menu and the menu with the given name.  If the
        named menu is a sub-menu, its parent will be transitioned to, but the sub-menu will have control.
        The new menu will become active on the next frame.
        
        If C{None} is passed instead of a menu name, the game will transition into the current level.
        
        @type  m:           C{L{Menu<UI.Menu.Menu.Menu>} | str | None}
        @param m:           Menu object or name of the menu to transition to.  If C{None}, it will transition
                            to the current level.
        """
        if isinstance(m, str) or isinstance(m, unicode):
            menu = self._menuDict[m]
        else:
            menu = m
        
        if menu == None:
            self._nextDisplayMenu = None
            # transitioning to gameplay, exit menu
            if self.CurrentMenu:
                self.CurrentMenu.OnExit()
        else:
            self._nextControlMenu = menu
            # make sure the display menu is not a sub-menu
            self._nextDisplayMenu = self._nextControlMenu.OldestParentMenu()
            
        if self.CurrentMenu == None:
            # go directly to the menu
            self._displayMenu = self._nextDisplayMenu
            self._controlMenu = self._nextDisplayMenu
            self._controlMenu.SwitchControlTo(self._controlMenu.Name)
            self._controlMenu.OnEnter()
        
    def Run(self):
        """
        Runs the update loop of the game until a C{Quit} C{U{event<http://www.pygame.org/docs/ref/event.html>}}
        is encountered.
        
        The loop includes:
            - gather input
            - update logic
            - draw
        """
        quit = False
        
        while (not quit):
            dt = self._clock.tick(self._maxFPS) / 1000.0
            #print 'FPS :', self._clock.get_fps()
            
            # when FPS drops, this creates slow down instead of dropped frames
            dt = 1.0 / self._maxFPS
            
            # alternate keyboard processing - cad
            keyboardInput = pygame.key.get_pressed()
            for controller in self.Controllers:
                controller.UpdateKeys(keyboardInput)
            
            # have all our events to process, clear the rest out to prevent overflow
            pygame.event.clear()
            
            if (self.CurrentMenu):
                # do menu stuff
                self.CurrentMenu.Update(dt)                
                self.CurrentMenu.DrawTo(Camera.windowSurf)

                # check if we should switch menus
                if self._nextControlMenu != self._controlMenu:
                    self._controlMenu.SwitchControlTo(self._nextControlMenu.Name)
                    self._controlMenu.OnExit()
                    self._nextControlMenu.OnEnter()
                
                self.CurrentMenu = self._nextDisplayMenu
                self._controlMenu = self._nextControlMenu
                
            
            elif (self.CurrentMap):
                #logic
                self.CurrentMap.Update(dt)
                #render
                self.CurrentMap.Draw()
                
                
                self.CheckPause()
                self.CheckMapEnd()
                
            pygame.display.flip()

            # check for a quit
            if pygame.event.get(QUIT):
                quit = True
            else:
                for controller in self.Controllers:
                    if controller.HasButton(Constants.ControllerConstants.QUIT_BUTTON) and controller.Button(Constants.ControllerConstants.QUIT_BUTTON).Down:
                        quit = True
                        break
                

    def CheckPause(self):
        """
        B{[Stub]} Function used to check when the game should be paused and what happens when it's paused.
        """
        return
                        
    def CheckMapEnd(self):
        """
        B{[Stub]} Function used to check when the current map is completed and what should be done when it finishes.
        """
        return

    def __map_path_by_index__(self, index):
        """
        Gets the map file path by its position in the map list.
        
        @type  index:    C{int}
        @param index:    The index of map.
        
        @rtype:          C{str}
        @return:         The file path to the specified map.
        """
        if (index >= len(self._mapPathList)):
                raise Exception('Map ' + index.__str__() + ' not found.  Check that it is being loaded first.')
        else:
            return self._mapPathList[index]
        
    def __map_path_by_name__(self, name):
        """
        Gets the map file path by its filename.
        
        @type  name:     C{str}
        @param name:     The filename of map.
        
        @rtype:          C{str}
        @return:         The file path to the specified map.
        """
        if (self._mapPathDict.has_key(name)):
            return self._mapPathDict[name]
        else:
            raise Exception('Map "' + name + '" not found.  Check that it is being loaded first.')
        
    def GetMenu(self, name):
        """
        Gets the menu by its name.
        
        @type  name:     C{str}
        @param name:     The name of the menu.
        
        @rtype:          L{Menu<UI.Menu.Menu.Menu>}
        @return:         Specified menu.
        """
        if (self._menuDict.has_key(name)):
            return self._menuDict[name]
        else:
            raise Exception('Menu "' + name + '" not found.  Check that it is being loaded first.')
        
    ############### PROPERTIES ###############

    def __get_controllers__(self):
        return self._controllers
    
    def __get_map__(self):
        return self._map
    def __set_map__(self, value):
        self._map = value
    
    def __get_current_menu__(self):
        return self._displayMenu
    def __set_current_menu__(self, value):
        self._displayMenu = value
        
    Controllers = property(__get_controllers__, None, None, "A C{list} of L{Controller<Utilities.Controller.Controller.Controller>}s that can input to the game.")
    CurrentMap = property(__get_map__, __set_map__, None, "Current L{GameMap<GameMap.GameMap>} being played.")
    CurrentMenu = property(__get_current_menu__, __set_current_menu__, None, "Currently active L{Menu<UI.Menu.Menu.Menu>}.")