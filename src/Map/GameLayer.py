'''
B{[Base Class]} A layer from the .TMX map file.

@author: Chris Alvarado-Dryden
'''

class GameLayer(object):
    """
    B{[Base Class]} A layer from the .TMX map file.  Similar to a L{GameMap<Map.GameMap.GameMap>}'s map
    specific data, it holds layer specific details and the objects that populate it.  It comes in two
    varieties to match the layers in U{Tiled<http://mapeditor.org/>} maps:
    
        - L{GameTileLayer<GameTileLayer.GameTileLayer>} for Layers
        - L{GameObjectLayer<GameObjectLayer.GameObjectLayer>} for Object Groups
    
    @note:  In the Tiled editor, entire layers can be moved.  Tiles that no longer fall within the map
            boundaries will not be loaded.  However, Object Group objects will still be loaded even outside
            of boundaries.
    
    @type visible:        C{bool}
    @ivar visible:        C{True} if the layer should be drawn, C{False} otherwise.
    
    @type _widthTiles:    C{int}
    @ivar _widthTiles:    How many L{GameTile<GameTile.GameTile>}s wide the layer is.
    
    @type _heightTiles:   C{int}
    @ivar _heightTiles:   How many L{GameTile<GameTile.GameTile>}s high the layer is.
    
    @type _widthPixels:   C{int}
    @ivar _widthPixels:   How many pixels wide the layer is.
    
    @type _heightPixels:  C{int}
    @ivar _heightPixels:  How many pixels high the layer is.
    
    @type _drawList:      C{list}
    @ivar _drawList:      All of the drawable objects in the layer as a single list.  Used for drawing.

    @type _name:          C{str}
    @ivar _name:          The name of the layer, from the U{Tiled<http://mapeditor.org/>} .TMX file.
    
    @type _map:           L{GameMap<Map.GameMap.GameMap>}                      
    @ivar _map:           The L{GameMap<Map.GameMap.GameMap>} this layer is in.
    """

    def __init__(self, loaderLayer, loaderTileMap, map):
        """
        Creates a GameLayer from the data structures
        U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>} makes.
        
        @type  loaderLayer:      L{TileLayer<tiledtmxloader.TileLayer>}
        @param loaderLayer:      Layer data structure from the loader.
        
        @type  loaderTileMap:    L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:    Map data structure created by the loader.
        
        @type  map:              L{GameMap<Map.GameMap.GameMap>}
        @param map:              The L{GameMap<Map.GameMap.GameMap>} this layer is in.
        """
        self.visible = loaderLayer.visible
        
        self._map = map
        
        # layer in tile dimensions
        self._widthTiles = loaderTileMap.width
        self._heightTiles = loaderTileMap.height
        
        # layer in pixel dimensions
        self._widthPixels = loaderTileMap.pixel_width
        self._heightPixels = loaderTileMap.pixel_height
        
        # tile dimensions
        self._tileWidth = loaderTileMap.tilewidth
        self._tileHeight = loaderTileMap.tileheight

        self._drawList = list()
        
        self._name = loaderLayer.name
        
        # other properties could be added here
        
        # load the map into our own data structures
        self.__load_layer__(loaderLayer, loaderTileMap)
        
    def __load_layer__(self, loaderLayer, loaderTileMap):
        """
        B{[Stub]} Loads the data from the U{tiledtmxloader<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>}
        data structures into our own.
        
        This is a stub, and should be implemented in child classes.
        
        @type  loaderLayer:    L{TileLayer<tiledtmxloader.TileLayer>}
        @param loaderLayer:    Layer data structure from the loader.
        
        @type  loaderTileMap:  L{TileMap<tiledtmxloader.TileMap>}
        @param loaderTileMap:  The data structure created by the loader.
        """
        return
    
    def Draw(self, cameras):
        """
        If visible, sends all of this layer's drawable objects to each listed
        camera to be drawn.
        
        @type  cameras:    C{list}
        @param cameras:    All of the L{Camera<Camera.Camera>}s to try to draw to.
        """
        if (not self.visible):
            return

        for item in self._drawList:
            item.Draw(cameras)
    
    def __str__(self):
        """
        Name of the layer.
        
        @rtype:     C{str}
        @return:    String representation of the GameLayer.
        """
        return self.Name
    
    ############### PROPERTIES ###############            
    
    def __get_width_tiles__(self):
        return self._widthTiles
    def __get_height_tiles__(self):
        return self._heightTiles
    def __get_width_pixels__(self):
        return self._widthPixels
    def __get_height_pixels__(self):
        return self._heightPixels
    def __get_name__(self):
        return self._name
    def __set_name__(self, value):
        self._name = value
    def __get_map__(self):
        return self._map

    WidthInTiles = property(__get_width_tiles__, None, None, "How many L{GameTile<GameTile.GameTile>}s wide the layer is.")
    HeightInTiles = property(__get_height_tiles__, None, None, "How many L{GameTile<GameTile.GameTile>}s high the layer is.")
    WidthInPixels = property(__get_width_pixels__, None, None, "How many pixels wide the layer is.")
    HeightInPixels = property(__get_height_pixels__, None, None, "How many pixels high the layer is.")
    Name = property(__get_name__, __set_name__, None, "The name of the layer, from the U{Tiled<http://mapeditor.org/>} .TMX.")
    Map = property(__get_map__, None, None, "The L{GameMap<Map.GameMap.GameMap>} this layer is on.")