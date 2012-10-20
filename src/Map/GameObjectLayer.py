'''
A layer of L{SpawnPoint<SpawnPoint.SpawnPoint>}s in a L{GameMap<GameMap.GameMap>}.

@author: Chris Alvarado-Dryden
'''

from Map.GameLayer import GameLayer
from SpawnPoint import SpawnPoint

from Utilities.Camera import Camera
from Core.CollisionGroup import CollisionGroup

class GameObjectLayer(GameLayer):
    """
    A layer of L{SpawnPoint<SpawnPoint.SpawnPoint>}s in a L{GameMap<GameMap.GameMap>}. Each of these layers
    match up with the Object Group layers in a U{Tiled<http://mapeditor.org/>} .TMX map file.
    
    Unlike L{GameTileLayer<Map.GameTileLayer.GameTileLayer>}s, the objects themselves are not meant to be
    manipulated from the layer, but instead from the L{GameMap<Map.GameMap.GameMap>}.
    
    @type _spawnList:    C{list}
    @ivar _spawnList:    A list of L{SpawnPoint<SpawnPoint.SpawnPoint>}s, each corresponding to an object
                         from the Tiled Object Group.
    """

    def __init__(self, loaderObjGroup, loaderTileMap, map):
        """
        Creates a GameObjectLayer from the data structures
        U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>} makes.
        
        @type  loaderObjGroup:    L{MapObjectGroup<tiledtmxloader.MapObjectGroup>}
        @param loaderObjGroup:    Layer data structure from the loader.
        
        @type  loaderTileMap:     L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:     Map data structure created by the loader.        
        
        @type  map:               L{GameMap<Map.GameMap.GameMap>}
        @param map:               The L{GameMap<Map.GameMap.GameMap>} this layer is in.
        """
        
        self._spawnList = []
        
        GameLayer.__init__(self, loaderObjGroup, loaderTileMap, map)
        
        
    def __load_layer__(self, loaderObjGroup, loaderTileMap):
        """
        Creates L{SpawnPoint<SpawnPoint.SpawnPoint>}s from the U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>}
        objects and places them into our own data structures.
        
        Object Groups will appear in game as they appear in the editor. If they have been moved in the editor and objects appear
        to be out of bounds, they will B{still} appear in game.
        
        @type  loaderObjGroup:     L{MapObjectGroup<tiledtmxloader.MapObjectGroup>}
        @param loaderObjGroup:     Object group structure from the loader.
        
        @type  loaderTileMap:      L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:      The data structure created by the loader.
        """
        
        for obj in loaderObjGroup.objects:
            type = obj.type
            coords = (obj.x + (loaderObjGroup.x * loaderTileMap.tilewidth) , obj.y + (loaderObjGroup.y * loaderTileMap.tileheight))
            props = obj.properties
            # put everything in properties
            props[u'name'] = obj.name
            props[u'type'] = obj.type
            props[u'x'] = coords[0]
            props[u'y'] = coords[1]
            props[u'width'] = obj.width
            props[u'height'] = obj.height
            
            #self._spawnList.append(SpawnPoint(type, coords, props))
            self._spawnList.append(SpawnPoint(type, props))
            
    def SpawnObjects(self):
        """
        Spawns one instance of each object from the L{SpawnList}.  Also adds the spawned object to the draw list unless
        it is a L{Camera<Utilities.Camera.Camera>} or L{CollisionGroup<CollisionGroup.CollisionGroup>}.
        
        @rtype:    C{list}
        @return:   A list of all objects spawned.
        """
        objects = []
        for spawn in self._spawnList:
            obj = spawn.Spawn()
            if (not isinstance(obj, Camera) and not isinstance(obj, CollisionGroup)):
                self._drawList.append(obj)
            objects.append(obj)
            
        return objects
    
    ############### PROPERTIES ###############
    def __get_spawnList__(self):
        return self._spawnList
    
    SpawnList = property(__get_spawnList__, None, None, "C{list} of L{SpawnPoint<SpawnPoint.SpawnPoint>}s on this layer.")