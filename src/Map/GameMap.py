"""
A map created using U{Tiled<http://mapeditor.org/>} (Java version 0.7.2 supported).

@author: Chris Alvarado-Dryden
"""
from Core import Constants
import pygame.image
import Utilities.HelperFunctions

from Map.GameTileLayer import GameTileLayer
from Map.GameObjectLayer import GameObjectLayer
from Utilities.tiledtmxloader import *
from Utilities.vector import Vector
from Core.Player import Player
from Utilities.Camera import Camera
from Core.MusicPlayer import MusicPlayer
from UI.Panel import Panel

class GameMap(object):
    """
    The GameMap class describes a single map within the game.  It is comprised of named L{GameLayer<GameLayer.GameLayer>}s,
    which are collections of tiles (L{GameTileLayer<GameTileLayer.GameTileLayer>}) or game objects (L{GameObjectLayer<GameObjectLayer.GameObjectLayer>}).
    It also holds map specific constants and properties like gravity.
    
    Because the map holds data about the environment and its inhabitants, it runs the logic and draw portions of the game loop.
    On top of that, it also processes map level UI elements with an internal full screen L{Panel<UI.Panel.Panel>}.
    
    To load a map, a modified version of U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>} is used.
    
    @see: Maps are created using U{Tiled<http://mapeditor.org/>} (Java version 0.7.2 supported).  A tutorial on making a map can be found
    U{here<http://eventually-i-promise.com/>} (eventually).
    
    @type gravity:                  C{Vector}
    @ivar gravity:                  The force applied to all objects in the game.  A default value can be set in 
                                    L{Constants.MapConstants.DEFAULT_GRAVITY} or the value can be overridden in the editor
                                    via Map Properties.  See the U{map tutorial<http://eventually-i-promise.com>}
                                    for more information (eventually).
    
    @type _data:                    L{TileMap<tiledtmxloader.TileMap>}
    @ivar _data:                    Holds the important map data from the map loader.
    
    @type _layerNameMappings:       C{dict} 
    @ivar _layerNameMappings:       C{{str : int}} - A mapping between layer names and their positions in the layer list.
    
    @type _tileLayers:              C{list}
    @ivar _tileLayers:              A list of all L{GameTileLayer<GameTileLayer.GameTileLayer>}s in this map.
    
    @type _objectLayers:            C{list}
    @ivar _objectLayers:            A list of all L{GameObjectLayer<GameObjectLayer.GameObjectLayer>}s in this map.
    
    @type _layers:                  C{list}
    @ivar _layers:                  A list of all L{GameLayer<GameLayer.GameLayer>}s in this map.
    
    @type _players:                 C{dict}
    @ivar _players:                 C{{str : L{Player<Player.Player>}}} - All Players in this map, keyed by name.
    
    @type _nonPlayerActors:         C{dict}
    @ivar _nonPlayerActors:         C{{str : L{Actor<Actor.Actor>}}} - All Actors in this map I{except Players}, keyed by name.
    
    @type _allActors:               C{dict}
    @ivar _allActors:               C{{str : L{Actor<Actor.Actor>}}} - All Actors in this map I{including Players}, keyed by name.
    
    @type _collisionGroups:         C{dict}
    @ivar _collisionGroups:         C{{str : L{CollisionGroup<CollisionGroup.CollisionGroup>}}} - All collision groups in
                                    the map, keyed by their names.
    
    @type _cameraDict:              C{dict}
    @ivar _cameraDict:              C{{str : L{Camera<Utilities.Camera.Camera>}}} - All active cameras in the map, keyed by name.
    
    @type _bg:                      U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _bg:                      Background image for this map.
    
    @type _bgColor:                 U{pygame.Color<http://www.pygame.org/docs/ref/color.html>}
    @ivar _bgColor:                 Color to wipe the scene with each frame.
    
    @type _path:                    C{str}
    @ivar _path:                    File path to the location of the .TMX file.  Used when loading/reloading maps.
    
    @type WantsToSwitchMap:         C{bool}
    @ivar WantsToSwitchMap:         Used to notify the L{Game<Game.Game>} when maps should be switched.  C{True} if the game
                                    should switch maps, C{False} otherwise.
    
    @type _mapSwitchParams:         C{(int | str, bool)}
    @ivar _mapSwitchParams:         Used to tell the L{Game<Game.Game>} how maps should be switched.  First element is either map
                                    number or map file name, second is if data should be transfered from this map to the next.
                                    
    @type _musicLoaded:             C{bool}
    @ivar _musicLoaded:             C{True} if background music was loaded for this map, C{False} otherwise.
    
    @type _musicPlayer:             L{MusicPlayer<MusicPlayer.MusicPlayer>}
    @ivar _musicPlayer:             Used to control music play back (background music).  Because this is a singleton, it is shared
                                    by all classes in the game.
                                    
    @type _panel:                   L{Panel<UI.Panel.Panel>}                                                                        
    @ivar _panel:                   A panel that covers the entirety of window while the map is being played.                                 
                                                                                                                                    
    @type _uiPaths:                 C{list}                                                                                         
    @ivar _uiPaths:                 List of file paths (C{str}) relative to the location of this map's .TMX file, where map level
                                    UI elements are stored.
    """

    def __init__(self, path, controllers=None, transferMap=None):
        """
        Loads the .TMX file at the given path, and creates all the necessary data structures to support it.
        
        @type  path:     C{str}
        @param path:     The file path to the location of the .TMX file.
        
        @type  controllers:        C{list | None}
        @param controllers:        L{Controller<Utilities.Controller.Controller>}s which will be bound to any
                                   L{Player<Player.Player>}s in this map.
        
        @type  transferMap:        C{GameMap | None}
        @param transferMap:        Map to use for transferring objects into this map.
        """
        # path to reload from
        self._path = path
        
        # loader calls
        loaderMap = TileMapParser().parse_decode(path)
        loaderMap.load(ImageLoaderPygame())
        
        self._data = loaderMap
        
        self._tileLayers = []
        self._objectLayers = []
        self._layerNameMappings = {}
        
        # convert to our own data structure
        self.__convert_tile_map__(loaderMap)
        
        # look for map properties
        
        # gravity
        if (Constants.EditorConstants.MAP_PROP_GRAVITY in loaderMap.properties and loaderMap.properties[Constants.EditorConstants.MAP_PROP_GRAVITY].strip()):
            gravTuple = tuple(int(n) for n in (loaderMap.properties[Constants.EditorConstants.MAP_PROP_GRAVITY])[1:-1].split(','))
        else:
            gravTuple = Constants.MapConstants.DEFAULT_GRAVITY
            
        self.gravity = Vector(gravTuple)
        
        # background
        if (Constants.EditorConstants.MAP_PROP_BACKGROUND in loaderMap.properties and loaderMap.properties[Constants.EditorConstants.MAP_PROP_BACKGROUND].strip()):
            bgPath = str(loaderMap.properties[Constants.EditorConstants.MAP_PROP_BACKGROUND])
            # pull off the file from path and create bg path
            bgPath = os.path.normpath(os.path.join(os.path.dirname(path), bgPath))
            self._bg = pygame.image.load(bgPath)
            self._bg.convert_alpha()
        else:
            self._bg = None
            
        # background color
        if (Constants.EditorConstants.MAP_PROP_BACKGROUND_COLOR in loaderMap.properties and loaderMap.properties[Constants.EditorConstants.MAP_PROP_BACKGROUND_COLOR].strip()):
            colorStr = str(loaderMap.properties[Constants.EditorConstants.MAP_PROP_BACKGROUND_COLOR])
            colorTup = Utilities.HelperFunctions.StringConversions.StringToIntTuple(colorStr)
            # unpack it
            if (len(colorTup) < 3 or len(colorTup) > 4):
                propName = Constants.EditorConstants.MAP_PROP_BACKGROUND_COLOR
                raise Exception('Check map file "' + self.FileName + '": Map Property "' + propName + '" must have either 3 or 4 values.')
            self._bgColor = pygame.Color(*colorTup)
        else:
            self._bgColor = Constants.MapConstants.DEFAULT_CLEAR_COLOR
        
        # music
        self._musicLoaded = False
        self._musicPlayer = MusicPlayer()
        
        if (Constants.EditorConstants.MAP_PROP_MUSIC in loaderMap.properties and loaderMap.properties[Constants.EditorConstants.MAP_PROP_MUSIC].strip()):
            musicPath = str(loaderMap.properties[Constants.EditorConstants.MAP_PROP_MUSIC])
            musicPath = os.path.normpath(os.path.join(os.path.dirname(path), musicPath))

            self._musicPlayer.Load(musicPath)
            self._musicLoaded= True
            
        # ui
        self._panel = Panel((0, 0), Camera.windowSurf.get_width(), Camera.windowSurf.get_height())
        Camera.windowPanel.AddChild(self._panel)
        self._uiPaths = []
        if (Constants.EditorConstants.MAP_PROP_UI_FILES in loaderMap.properties and loaderMap.properties[Constants.EditorConstants.MAP_PROP_UI_FILES].strip()):
            uiPaths = map(unicode.strip, loaderMap.properties[Constants.EditorConstants.MAP_PROP_UI_FILES].split(','))
            for uiPath in uiPaths:
                self._uiPaths.append(os.path.normpath(os.path.join(os.path.dirname(path), uiPath)))
        
        # the kinds of map objects in the editor
        self._players = {}
        self._nonPlayerActors = {}
        self._allActors = {}
        self._collisionGroups = {}
        self._cameraDict = {}
        
        # map switching
        self.WantsToSwitchMap = False
        self._mapSwitchParams = (Constants.GameConstants.NEXT_MAP, False)
        
        if controllers:
            self.__load_objects__(controllers, transferMap)
        
        self.__load_ui__()

    def Reload(self):
        """
        Recreates the GameMap.  After being called it will be as if the map was just instantiated.
        """
        self.RemoveUI()
        # soooooooooooo dirty
        self = self.__init__(self._path)
        
    def Restart(self, controllers, transferMap):
        """
        Restarts the GameMap with the given Controllers, and loads objects based on the given transfer
        map.
        
        @type  controllers:        C{list}
        @param controllers:        L{Controller<Utilities.Controller.Controller>}s which will be bound to any
                                   L{Player<Player.Player>}s in this map.
        
        @type  transferMap:        C{GameMap}
        @param transferMap:        Map to use for transferring objects into this map.
        """
        self.Reload()
        self.__load_objects__(controllers, transferMap)
        self.__load_ui__()
        
    def SwitchToMap(self, mapName, transfer=True):
        """
        Requests to change from this map to the map with the given name or index.  If C{transfer} is set, some object
        data will be transfered to the next map.
        
        @type  mapName:        C{str or int}
        @param mapName:        File name (C{'example.tmx'}) or map number of the map to switch to.
        
        @type  transfer:       C{bool}
        @param transfer:       C{True} if this map should be used to transfer data to the next, C{False} otherwise.
        """
        self.WantsToSwitchMap = True
        self._mapSwitchParams = (mapName, transfer)

    def __convert_tile_map__(self, loaderTileMap):
        """
        Converts U{tiledtmxloader's<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>} data structures into our own.
        Populates the list of GameLayers, creates a dictionary to map layer names to layer indexes, and populates the tile and object
        layer lists.
        
        @type  loaderTileMap:    L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:    The data structure created by the loader.
        """
        layers = []
        layerNames = []
        
        # get all of the Tile Layers
        for layer in loaderTileMap.layers:
            layerNames.append(layer.name)
            gtl = GameTileLayer(layer, loaderTileMap, self)
            self._tileLayers.append(gtl)
            layers.append(gtl)
            
        # get all of the Object Layers    
        for objLayer in loaderTileMap.object_groups:
            index = objLayer.order
            layerNames.insert(index, objLayer.name)
            gol = GameObjectLayer(objLayer, loaderTileMap, self)
            self._objectLayers.append(gol)
            layers.insert(index, gol)
        
        self.__populate_layer_name_dict__(layerNames)
        
        self._layers = layers
    
    def __load_objects__(self, controllers, fromMap=None):
        """
        Loads all Map Objects from the L{GameObjectLayer<GameObjectLayer.GameObjectLayer>}s.  This includes players, actors,
        collision groups, and cameras.  If C{fromMap} is set, it will be used to transfer object data into this map's objects.
        
        For players, collision groups, and cameras there is special loading to accommodate their properties.
        
        @type  controllers:        C{list}
        @param controllers:        List of L{Controller<Utilities.Controller.Controller>}s that can be associated with
                                   L{Player<Player.Player>}s.
                                   
        @type  fromMap:            C{GameMap}
        @param fromMap:            Map to use for transferring objects into this map.
        """
        # basic collision group setup
        cgroupLayer = self.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_GROUPS)
        self.__load_collision_groups__(cgroupLayer)
        
        # look to refactor - CAD
        
        # cameras
        cameraLayer = self.Layer(Constants.EditorConstants.LAYER_NAME_CAMERAS)
        cameras = cameraLayer.SpawnObjects()
        for camera in cameras:
            self.AddCamera(camera)
        
        # look for spawn points in the object layers
        for layer in self.ObjectLayers:
            
            # skip collision group layer, it's already loaded
            if layer is cgroupLayer or layer is cameraLayer:
                continue
            
            objects = layer.SpawnObjects()
            for obj in objects:
                
                # populate collision groups
                # assumes they are Actors
                for objCGroupName in obj.cgroupNames:
                    cgroup = self._collisionGroups[objCGroupName]
                    cgroup.AddMember(obj)
                
                # check if it should be a camera target
                for cam in self.__get_untargetted_cameras__():
                    if cam.targetName == obj.Name:
                        cam.Target = obj
                
                # pick out Players to give them controllers and add to player list
                if isinstance(obj, Player):
                    if (obj.PlayerNum < 0 or obj.PlayerNum >= len(controllers)):
                        raise Exception('Check map file: Controller not found for Player ' + (obj.PlayerNum + 1).__str__()) 
                    obj.Controller = controllers[obj.PlayerNum]
                    self.AddPlayer(obj, layer)
                
                # add the other objects (Actors)
                else:
                    self.AddActor(obj, layer)
                    
                if fromMap and obj._transferFromName:
                    # look for object on previous map to transfer from
                    if fromMap._allActors.has_key(obj._transferFromName):
                        # do transfer
                        obj.TransferFrom(fromMap._allActors[obj._transferFromName])
                    else:
                        # handle not transfer
                        pass 
                    
        # all done, see if there are any cameras without a target and throw an error
        if len(self.__get_untargetted_cameras__()) > 0:
            errorBegin = 'Check map file "' + self.FileName + '": The following Cameras could not find their targets:\n'
            camAndTargets = ''
            for cam in self.__get_untargetted_cameras__():
                camAndTargets += '"' + cam.Name + '" - "' + cam.targetName + '"\n'
                
            raise Exception(errorBegin + camAndTargets)

    def __load_collision_groups__(self, cgroupLayer):
        """
        Loads the L{CollisionGroup<CollisionGroup.CollisionGroup>} objects and populates L{_collisionGroups}.  Collision Groups
        will be empty after this call, but their references to each other will have been made. 
        
        @type  cgroupLayer:    L{GameObjectLayer<Map.GameObjectLayer.GameObjectLayer>}
        @param cgroupLayer:    Layer containing all CollisionGroups.
        """
        # setup collision groups
        cgroups = cgroupLayer.SpawnObjects()
        
        # associate names to groups
        for cgroup in cgroups:
            self._collisionGroups[cgroup.Name] = cgroup
        
        # coordinate which group collides with which
        for cgroup in cgroups:
            cgroup.__assign_collision_groups__(self._collisionGroups)
        
    def __get_untargetted_cameras__(self):
        """
        Returns a list of L{Camera<Utilities.Camera.Camera>}s that should have targets but do not.
        
        @rtype:    C{list}
        @return:   List of Cameras that should have targets but do not.
        """
        withoutTarget = []
        for camera in self.Cameras:
            if camera.Target == None:
                withoutTarget.append(camera)
        return withoutTarget
    
    def __load_ui__(self):
        """
        Loads all UI L{Panel<UI.Panel.Panel>}s that are attached to L{Camera<Utilities.Camera.Camera>}s.
        """
        # cad load UIs for cameras - maybe move this?
        for camera in self.Cameras:
            camera.LoadUIs()
        
        for path in self._uiPaths:
            self._panel.AddChild(Panel.PanelFromXML(path, Constants.GameConstants.BASE_PATH, self))
            
    def RemoveUI(self):
        """
        Unloads all UI L{Panel<UI.Panel.Panel>}s that are attached to L{Camera<Utilities.Camera.Camera>}s.
        """
        for camera in self.Cameras:
            camera.UnloadUIs()
    
    def AddPlayer(self, player, layer):
        """
        Add the given player to the map.
        
        @type  player:    L{Player<Player.Player>}
        @param player:    Player to add to the map.
        """
        if (self._players.has_key(player.Name)):
            raise Exception('Check map file "' + self.FileName + '":  Player "' + player.Name + '" already exists.')
        self._players[player.Name] = player
        player.Map = self
        player.Layer = layer
        
        self.AddActor(player, layer)

    def AddActor(self, actor, layer):
        """
        Add the given actor to the map.
        
        @type  actor:    L{Actor<Actor.Actor>}
        @param actor:    Actor to add to the map.
        
        @type  layer:    L{GameObjectLayer<Map.GameObjectLayer.GameObjectLayer>}
        @param layer:    Layer the actor resides in.
        """
        if (self._allActors.has_key(actor.Name)):
            raise Exception('Check map file "' + self.FileName + '":  Actor "' + actor.Name + '" already exists.')
        else:
            self._allActors[actor.Name] = actor
            
            if (not isinstance(actor, Player)):
                self._nonPlayerActors[actor.Name] = actor
                actor.Map = self
                actor.Layer = layer
        
    def AddCamera(self, camera):
        """
        Adds the given camera to this map's list of cameras.
        
        @type  camera:    L{Camera<Utilities.Camera.Camera>}
        @param camera:    Camera to add to this map.
        """
        self._cameraDict[camera.Name] = camera
        camera.Map = self
    
    def __populate_layer_name_dict__(self, nameList):
        """
        Populates instance variable L{_layerNameMappings<GameMap.GameMap._layerNameMappings>}.
        
        @type  nameList:    C{list}
        @param nameList:    A list of names for the layers, taken from the .TMX layer names.
        """
        for i in range(len(nameList)):
            self._layerNameMappings[nameList[i]] = i
    
    def Layer(self, l):
        """
        Gets the specified L{GameLayer<GameLayer.GameLayer>}.
        
        @type  l:    C{str} or C{int}
        @param l:    Either a layer name or index.
        
        @rtype:      L{GameLayer<GameLayer.GameLayer>}
        @return:     Specified layer.
        """
        if (isinstance(l, str) and not l.isdigit()):
            return self.__layer_by_name__(l)
        else:
            return self.__layer_by_index__(int(l))
    
    def __layer_by_index__(self, index):
        """
        Gets the layer by its position in the layer list.
        
        @type  index:    C{int}
        @param index:    The index of layer.
        
        @rtype:          L{GameLayer<GameLayer.GameLayer>}
        @return:         Specified layer.
        """
        return self._layers[index]
    
    def __layer_by_name__(self, name):
        """
        Gets the layer by its name.
        
        @type  name:    C{str}
        @param name:    The name of the layer.
        
        @rtype:         L{GameLayer<GameLayer.GameLayer>}
        @return:        Specified layer.
        """
        return self.__layer_by_index__(self._layerNameMappings[name])
    
    def WorldToTileCoords(self, v):
        """
        Converts world coordinates to tile coordinates (each tile is 1 unit).
        
        @type  v:    L{Vector<Utilities.vector.Vector>}
        @param v:    World coordinates to convert.
        
        @rtype:      C{(int, int)}
        @return:     Tile coordinate.
        """
        x = int(v.x / self.TileWidth)
        y = int(v.y / self.TileHeight)
        
        return (x,y)
    
    def TileToWorldCoords(self, xTile, yTile):
        """
        Converts tile coordinates (1 unit per tile) to world coordinates (1 unit per pixel).
        
        @type  xTile:    C{int}
        @param xTile:    X position in tile coordinates.
        
        @type  yTile:    C{int}
        @param yTile:    Y position in tile coordinates.
        
        @rtype:          L{Vector<Utilities.vector.Vector>}
        @return:         World coordinates of the top left corner at the tile position.
        """
        x = xTile * self.TileWidth
        y = yTile * self.TileHeight
        
        return Vector((x, y))
    
    def Update(self, dt):
        """
        Update logic for all L{Actor<Actor.Actor>}s in this map.  L{Player<Player.Player>}s are always updated first
        and L{Camera<Utilities.Camera.Camera>}s are updated last.
        
        @type  dt:    C{float}
        @param dt:    Time in seconds since the last frame refresh.
        """
        # update players first
        for player in self.Players:
            player.Update(dt)
            
        # then the rest of the objects
        for obj in self.NonPlayerActors:
            obj.Update(dt)
            
        # update cameras last
        for camera in self.Cameras:
            camera.Update(dt)
            
        # finally the map level UI
        self._panel.Update(dt)
    
    def Draw(self):
        """
        Send every visible L{GameLayer<GameLayer.GameLayer>} to this map's cameras
        to be drawn.
        """
        for camera in self.Cameras:
            camera.Clear(self._bgColor)

        if (self.Background):
            for camera in self.Cameras:
                self.__tile_background__(camera)

        for layer in self._layers:
            if layer.visible:
                layer.Draw(self.Cameras)
        
        for camera in self.Cameras:
            camera.DrawBorders()
            camera.FinalizeDraw()
            
        self._panel.DrawTo(Camera.windowSurf)
    
    def DrawLayer(self, cameras, layer):
        """
        Draw the given layer if it is visible.
        
        @type  cameras:      C{list}
        @param cameras:      All of the L{Camera<Utilities.Camera.Camera>}s to try to draw to.
        
        @type  layer:        L{GameLayer<GameLayer.GameLayer>}
        @param layer:        The layer to draw.
        """
        layer.Draw(cameras)

    def StopSounds(self):
        """
        Stops all L{Sound<Sound.Sound>}s associated with this GameMap and any music.
        """
        # can be used for pause maybe
        self._musicPlayer.Stop()
        
        for actor in self._allActors.values():
            actor.StopSounds()
        for layer in self.TileLayers:
            layer.StopSounds()
            
    def PauseSounds(self):
        """
        Pauses all L{Sound<Sound.Sound>}s associated with this GameMap and any music.
        """        
        self._musicPlayer.Pause()
        
        for actor in self._allActors.values():
            actor.PauseSounds()
        for layer in self.TileLayers:
            layer.PauseSounds()
            
    def ResumeSounds(self):
        """
        Resumes all L{Sound<Sound.Sound>}s associated with this GameMap and any music.
        """
        if self.MusicLoaded:
            self._musicPlayer.Play()
        
        for actor in self._allActors.values():
            actor.ResumeSounds()
        for layer in self.TileLayers:
            layer.ResumeSounds()
        
    def __tile_background__(self, camera):
        """
        Tiles the L{background image<Background>} and sends it to the camera to be drawn.
        
        @type  camera:    L{Camera<Utilities.Camera.Camera>}
        @param camera:    Camera to draw background to.
        """
        # starting point
        paintAtX, paintAtY = camera.boundingBox.topleft
        
        # while there's still room to paint
        while paintAtY < camera.boundingBox.bottom:
            
            # where in the background we should start drawing from
            bgY = paintAtY % self.Background.get_height()
            
            # how much texture we have to work with
            distBGEndY = self.Background.get_height() - bgY
            # how much room we have
            distDispEndY = camera.boundingBox.bottom - paintAtY
            # use the smaller for the subsurface
            paintY = min(distBGEndY, distDispEndY)
            
            while paintAtX < camera.boundingBox.right:
                bgX = paintAtX % self.Background.get_width()
                distBGEndX = self.Background.get_width() - bgX
                distDispEndX = camera.boundingBox.right - paintAtX
                paintX = min(distBGEndX, distDispEndX)
                
                # paint subsurface
                bgTile = self.Background.subsurface(pygame.Rect(bgX, bgY, paintX, paintY))
                camera.Draw(bgTile, (paintAtX, paintAtY))
                
                paintAtX += paintX
                
            paintAtY += paintY
            paintAtX = camera.boundingBox.left

    def __str__(self):
        """
        File name of the map.
        
        @rtype:     C{str}
        @return:    String representation of the GameMap.
        """
        return self.FileName

    ############### PROPERTIES ############### 

    def __get_file_path__(self):
        return self._path

    def __get_file_name__(self):
        return os.path.basename(self._path)

    def __get_width_in_tiles__(self):
        return self._data.width

    def __get_height_in_tiles__(self):
        return self._data.height
    
    def __get_width_in_pixels__(self):
        return self._data.pixel_width
    
    def __get_height_in_pixels__(self):
        return self._data.pixel_height
    
    def __get_tile_width__(self):
        return self._data.tilewidth
        
    def __get_tile_height__(self):
        return self._data.tileheight
    
    def __get_tileLayers__(self):
        return self._tileLayers
    
    def __get_objectLayers__(self):
        return self._objectLayers
    
    def __get_players__(self):
        sorted = self._players.values()
        sorted.sort(None, lambda player: player.PlayerNum)
        return sorted
    
    def __get_nonPlayerActors__(self):
        return self._nonPlayerActors.values()
    
    def __get_cameras__(self):
        cams = self._cameraDict.values()
        cams.sort(None, lambda camera: camera.Order)
        return cams
    
    def __get_bg__(self):
        return self._bg
    def __set_bg__(self, value):
        self._bg = value

    def __get_nextMapName__(self):
        return self._mapSwitchParams
    
    def __get_musicLoaded__(self):
        return self._musicLoaded
    def __set_music__(self, value):
        self._musicLoaded = value

    FilePath = property(__get_file_path__, None, None, "Full file path for this map.")
    FileName = property(__get_file_name__, None, None, "File name of this map, *.TMX.")
    WidthInTiles = property(__get_width_in_tiles__, None, None, "The width in number of tiles.")
    HeightInTiles = property(__get_height_in_tiles__, None, None, "The height in number of tiles.")
    WidthInPixels = property(__get_width_in_pixels__, None, None, "The width in pixels.")
    HeightInPixels = property(__get_height_in_pixels__, None, None, "The height in pixels.")
    TileWidth = property(__get_tile_width__, None, None, "The width of tiles in this map.")
    TileHeight = property(__get_tile_height__, None, None, "The height of tiles in this map.")
    TileLayers = property(__get_tileLayers__, None, None, "The L{GameTileLayer<Map.GameTileLayer.GameTileLayer>}s.")
    ObjectLayers = property(__get_objectLayers__, None, None, "The L{GameObjectLayer<Map.GameObjectLayer.GameObjectLayer>}s.")
    Players = property(__get_players__, None, None, "C{list} of L{Player<Player.Player>}s in the map.")
    NonPlayerActors = property(__get_nonPlayerActors__, None, None, "C{list} of all L{Actor<Actor.Actor>}s except L{Player<Player.Player>}s.")
    Cameras = property(__get_cameras__, None, None, "C{list} of L{Camera<Utilities.Camera.Camera>}s that are rendering to the screen.")
    Background = property(__get_bg__, __set_bg__, None, "Background image.")
    MapSwitchParameters = property(__get_nextMapName__, None, None, "Parameters used by L{Game<Game.Game>} when switching maps.")
    MusicLoaded = property(__get_musicLoaded__, None, None, "C{True} if background music was loaded, C{False} otherwise.")