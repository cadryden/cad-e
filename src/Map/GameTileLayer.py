'''
A layer of L{GameTile<GameTile.GameTile>}s in a L{GameMap<GameMap.GameMap>}.

@author: Chris Alvarado-Dryden
'''
from Core import Constants
import Utilities.HelperFunctions

from Map.GameLayer import GameLayer
from Map.GameTile import GameTile
from Utilities.vector import Vector

class GameTileLayer(GameLayer):
    """
    A layer of L{GameTile<GameTile.GameTile>}s in a L{GameMap<GameMap.GameMap>}.  Each of these layers match
    up with the tile layers in a U{Tiled<http://mapeditor.org/>} .TMX map file.
    
    @type _tileWidth:     C{int}
    @ivar _tileWidth:     The width of each L{GameTile<GameTile.GameTile>}.
    
    @type _tileHeight:    C{int}
    @ivar _tileHeight:    The height of each L{GameTile<GameTile.GameTile>}.
    
    @type _tileMatrix:    C{list}
    @ivar _tileMatrix:    All of the L{GameTile<GameTile.GameTile>}s in the layer, arranged as a 2D matrix.  Top left tile is C{[0,0]}.
                          Used for quickly switching between world and tile coordinates.
    """

    def __init__(self, loaderLayer, loaderTileMap, map):
        """
        Creates a GameTileLayer from the data structures
        U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>} makes.
        
        @type  loaderLayer:      L{TileLayer<tiledtmxloader.TileLayer>}
        @param loaderLayer:      Layer data structure from the loader.
        
        @type  loaderTileMap:    L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:    Map data structure created by the loader.
        
        @type  map:              C{str}
        @param map:              File path to the map this layer is in.
        """
        
        # tile dimensions
        self._tileWidth = loaderTileMap.tilewidth
        self._tileHeight = loaderTileMap.tileheight
        
        # the tiles
        self._tileMatrix = list()
        
        # tile layer properties
        self._animated = False
        if loaderLayer.properties.has_key(Constants.EditorConstants.LAYER_PROP_ANIMATED) and loaderLayer.properties[Constants.EditorConstants.LAYER_PROP_ANIMATED] == 'true':
            self._animated = True
        
        GameLayer.__init__(self, loaderLayer, loaderTileMap, map)

    
    def __load_layer__(self, loaderLayer, loaderTileMap):
        """
        Creates the L{GameTile<GameTile.GameTile>}s from the U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>}
        objects and places them into our own data structures.  If a tile has a I{type} property, it will be read and processed similarly to
        L{SpawnPoint<Map.SpawnPoint.SpawnPoint>}s/Map Objects.
        
        Layers will appear in game as they appear in the editor. If layers have been moved and clipped in the editor, those tiles B{will not}
        be loaded.
        
        @type  loaderLayer:    L{TileLayer<tiledtmxloader.TileLayer>}
        @param loaderLayer:    Layer data structure from the loader.
        
        @type  loaderTileMap:  L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:  Map data structure created by the loader.
        """
        gidmap = loaderLayer.decoded_content
        for xIndex in range(0, self.WidthInTiles):
            # check the layer offset from the editor
            adjustedX = xIndex - loaderLayer.x
            column = []
            
            for yIndex in range(0, self.HeightInTiles):
                adjustedY = yIndex - loaderLayer.y 
                
                if (adjustedX < 0 or adjustedY < 0 or adjustedX >= loaderLayer.width or adjustedY >= loaderLayer.height):
                    column.append(None)
                
                # normal procedure
                else:
                    gid = gidmap[(adjustedY) * loaderLayer.width + (adjustedX)]
                    if gid == 0:
                        column.append(None)
                    else:
                        tileType = GameTile
                        
                        # Tiles were loaded through 1 large image, special checks
                        if len(loaderTileMap.indexed_tiles[gid]) != 4:
                            junkA, junkB, surface = loaderTileMap.indexed_tiles[gid]
                            loaderTile = self.__get_tile_from_tilesets__(gid, loaderTileMap.named_tile_sets.values())
                        else:
                            # tiles created individually
                            junkA, junkB, surface, loaderTile = loaderTileMap.indexed_tiles[gid]
                        
                        # get the appropriate type of tile to construct    
                        if loaderTile and loaderTile.properties.has_key(Constants.EditorConstants.TILE_PROP_TYPE) and loaderTile.properties[Constants.EditorConstants.TILE_PROP_TYPE].strip():
                            typeName = loaderTile.properties[Constants.EditorConstants.TILE_PROP_TYPE]
                            tileType = Utilities.HelperFunctions.ReflectionFunctions.GetPythonClass(typeName)
                        
                        tile = tileType(loaderTile, surface, xIndex, yIndex, self)
                        column.append(tile)
                        self._drawList.append(tile)
            self._tileMatrix.append(column)
            
    def __get_tile_from_tilesets__(self, targetGid, tileSets):
        """
        Finds the loader L{Tile<tiledtmxloader.Tile>} with the given gid from all L{TileSet<tiledtmxloader.TileSet>}s in the map.
        If the Tile cannot be found, returns C{None}.
        
        @type  targetGid:        C{unicode}
        @param targetGid:        gid to search for.
        
        @type  tileSets:         L{TileSet<tiledtmxloader.TileSet>}
        @param tileSets:         All TileSets in this map.
        
        @rtype:                  C{L{Tile<tiledtmxloader.Tile>} | None}
        @return:                 Tile object to use for loading.
        """
        # sort the gids descending
        tileSets.sort(None, lambda tileSet: int(tileSet.firstgid), True)

        # check from highest to lowest gid
        for tileSet in tileSets:
            if int(tileSet.firstgid) <= targetGid:
                gid = targetGid - int(tileSet.firstgid)
                gid = unicode(gid)
                # search this set's tiles for a match
                for tile in tileSet.tiles:
                    if tile.id == gid:
                        return tile
                
        return None

    
    def Draw(self, cameras):
        """
        If visible, sends the tiles in the cameras view to be drawn.
        
        @type  cameras:    C{list}
        @param cameras:    All of the L{Camera<Camera.Camera>}s to try to draw to.
        """
        
        if (not self.visible):
            return

        if self.Animated:
            GameLayer.Draw(self, cameras)
            return

        graceTiles = Constants.CameraConstants.GRACE_TILES

        for camera in cameras:
            left, top = self.WorldToTileCoords(camera.boundingBox.topleft)
            right, bottom = self.WorldToTileCoords(camera.boundingBox.bottomright)
            
            
            left -= graceTiles
            right += graceTiles
            top -= graceTiles
            bottom += graceTiles
            
            while top <= bottom:
                for i in range(left, right + 1):
                    tile = self.TileAtIndex(i, top)
                    if tile:
                        tile.Draw(cameras)
                top += 1

    def TileAtIndex(self, x, y):
        """
        Gets the L{GameTile<GameTile.GameTile>} at the given tile coordinates.
        If the space is empty, returns C{None}.
        
        @type  x:    C{int}
        @param x:    The X tile coordinate (1 unit per GameTile).
        
        @type  y:    C{int}
        @param y:    The Y tile coordinate (1 unit per GameTile).
        
        @rtype:      C{L{GameTile<GameTile.GameTile>} | None}
        @return:     Tile at the given index, C{None} if no tile is present.
        """
        x = int(x)
        y = int(y)
        
        if (x >= self.WidthInTiles or x < 0 or y >= self.HeightInTiles or y < 0):
            #print 'tile [',x,'][',y,'] out of bounds'
            return None
        return self._tileMatrix[x][y]
    
    def TileAtCoord(self, v):
        """
        Gets the L{GameTile<GameTile.GameTile>} at the given world coordinates.
        If the space is empty, returns C{None}.
        
        @type  v:    L{Vector<Utilities.vector.Vector>}
        @param v:    World coordinates.
        
        @rtype:      C{L{GameTile<GameTile.GameTile>} | None}
        @return:     Tile at the given index, C{None} if no tile is present.
        """
        if (not isinstance(v, Vector)):
            v = Vector(v)
            
        x, y = self.WorldToTileCoords(v)
        
        return self.TileAtIndex(x, y)
    
    def TilesBetweenCoords(self, a, b):
        """
        Creates a C{list} of all L{GameTile<GameTile.GameTile>}s that intersect with a line
        segment from world coordinate C{a} to C{b}. 
        
        @note: Only horizontal and vertical lines are supported currently.
        
        @type  a:    L{Vector<Utilities.vector.Vector>}
        @param a:    Starting world coordinate.
        
        @type  b:    L{Vector<Utilities.vector.Vector>}
        @param b:    Ending world coordinate.
        
        @rtype:      C{list}
        @return:     Tiles between points C{a} and C{b} inclusive.
        """
        
        return self.TilesBetweenCoordsB(a, b)
        
        if (not isinstance(a, Vector)):
            a = Vector(a)
        if (not isinstance(b, Vector)):
            b = Vector(b)
        
        tiles = list()
        
        # start and end tiles
        start = self.TileAtCoord(a)
        end = self.TileAtCoord(b)
        
        if (start != None):
            tiles.append(start)
            # check if there's only 1 tile we're in
            if (start == end):
                return tiles
        
        # otherwise get the tiles between them
        # horizontal check
        if (a.y == b.y):
            step = self.TileWidth
            for i in range(a.x + step, b.x, step):
                tile = self.TileAtCoord(Vector((i, a.y)))
                if (tile != None):
                    tiles.append(tile)
        
        # vertical check        
        if (a.x == b.x):
            step = self.TileHeight
            for j in range(a.y + step, b.y, step):
                tile = self.TileAtCoord(Vector((a.x, j)))
                if (tile != None):
                    tiles.append(tile)
        
        if (end != None):
            tiles.append(end)
        
        return tiles
    
    def TilesBetweenCoordsB(self, a, b):
        """
        CAD a test to optimize TilesBetweenCoords by skipping directly to tile indices.
        """
        indexA = self.WorldToTileCoords(a)
        indexB = self.WorldToTileCoords(b)
        
        tiles = list()
        
        # start and end tiles
        start = self.TileAtIndex(indexA[0], indexA[1])
        end = self.TileAtIndex(indexB[0], indexB[1])
        
        if (start != None):
            tiles.append(start)
            # check if there's only 1 tile we're in
            if (start == end):
                return tiles
        
        # otherwise get the tiles between them
        # horizontal check
        if (indexA[1] == indexB[1]):
            for i in range(indexA[0] + 1, indexB[0]):
                tile = self.TileAtIndex(i, indexA[1])
                if (tile != None):
                    tiles.append(tile)
        
        # vertical check        
        if (indexA[0] == indexB[0]):
            for j in range(indexA[1] + 1, indexB[1]):
                tile = self.TileAtIndex(indexA[0], j)
                if (tile != None):
                    tiles.append(tile)
        
        if (end != None):
            tiles.append(end)
        
        return tiles
    
    def WorldToTileCoords(self, v):
        """
        Returns the X and Y tile index that holds the given world coordinate.
        
        @type  v:    L{Vector<Utilities.vector.Vector>}
        @param v:    The world coordinate to translate.
        
        @rtype:               C{(int, int)}
        @return:              The tile index of the given world coordinate.
        """
        
        x = int(v[0] / self.TileWidth)
        y = int(v[1] / self.TileHeight)
        
        return (x, y)
        

    def StopSounds(self):
        """
        Stops any L{Sound<Sound.Sound>}s that are being played by this layer's tiles.
        """
        for row in self._tileMatrix:
            for tile in row:
                if tile:
                    tile.StopSounds()
                    
    def PauseSounds(self):
        """
        Pauses any L{Sound<Sound.Sound>}s that are being played by this layer's tiles.
        """
        for row in self._tileMatrix:
            for tile in row:
                if tile:
                    tile.PauseSounds()
                    
    def ResumeSounds(self):
        """
        Resumes any L{Sound<Sound.Sound>}s that were being played by this layer's tiles.
        """
        for row in self._tileMatrix:
            for tile in row:
                if tile:
                    tile.ResumeSounds()
                    
    ############### PROPERTIES ###############
    def __get_tile_width__(self):
        return self._tileWidth
    def __get_tile_height__(self):
        return self._tileHeight
    def __get_animated__(self):
        return self._animated
    
    TileWidth = property(__get_tile_width__, None, None, "The width of each L{GameTile<GameTile.GameTile>}.")
    TileHeight = property(__get_tile_height__, None, None, "The height of each L{GameTile<GameTile.GameTile>}.")
    Animated = property(__get_animated__, None, None, "C{True} if this GameTileLayer can have animated L{GameTile<GameTile.GameTile>}s, C{False} otherwise.")
