'''
A tile in the L{GameMap<GameMap.GameMap>}, created and placed via U{Tiled<http://mapeditor.org/>}.

@author: Chris Alvarado-Dryden
'''
from Core import Constants
from Core.GameObject import GameObject
from Utilities.vector import LineSegment

class GameTile(GameObject):
    """
    A tile in the L{GameMap<GameMap.GameMap>}, created and placed via U{Tiled<http://mapeditor.org/>}.  They represent
    collision geometry, scenery, and other pieces of the environment.  While not completely static, they are not intended
    to update every frame.  If that is needed, see the L{Actor<Actor.Actor>} class.
    
    Individual GameTiles are accessible through L{GameTileLayer<GameTileLayer.GameTileLayer>}s. 
    """

    def __init__(self, loaderTile, surface, xIndex, yIndex, layer):
        """
        Create a new GameTile form the U{tiledtmxloader's<http://pygame.org/project-map+loader+for+'tiled'-1158-.html>}
        tile.
        
        @type  loaderTile:    L{Tile<tiledtmxloader.Tile>}
        @param loaderTile:    The the loader's tile object, which is converted to our own class.
        
        @type  surface:       C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @param surface:       This GameTile's graphic.
        
        @type  xIndex:        C{int}
        @param xIndex:        X coordinate in the Tiled editor.
        
        @type  yIndex:        C{int}
        @param yIndex:        Y coordinate in the Tiled editor. 
        
        @type  layer:         L{GameLayer<Map.GameLayer.GameLayer>}
        @param layer:         The GameLayer this tile is on.
        """
        rect = surface.get_rect()
        rect.topleft = (xIndex * rect.width, yIndex * rect.height)
        name = 'Game Tile'
        GameObject.__init__(self, rect.topleft, rect.width, rect.height, layer, name, surface)
        
        # When creating tiles from a large image, loader does not associate Tile objects with the surfaces.
        # Handling that.
        if loaderTile == None:
            self.properties = {}
        else:
            self.properties = loaderTile.properties
        
    def GetSegment(self, sideName):
        """
        Gets a L{LineSegment<Utilities.vector.LineSegment>} that represents one of the sides of this GameTile
        in world space.
        
        @type  sideName:    C{str}
        @param sideName:    Which side of the GameTile to get.  Valid side names are:
                                - C{'top'}
                                - C{'bottom'}
                                - C{'left'}
                                - C{'right'}
        
        @rtype:             L{LineSegment<Utilities.vector.LineSegment>}
        @return:            One side of the tile as a line segment.
        """
        topLeft = self.Position
        topRight = (topLeft[0] + self.Width, topLeft[1])
        bottomLeft = (topLeft[0], topLeft[1] + self.Height)
        bottomRight = (topRight[0], bottomLeft[1])
        
        segment = None
            
        if (sideName == Constants.TileConstants.SIDE_TOP):
            segment = LineSegment.from_points(topLeft, topRight)
        elif (sideName == Constants.TileConstants.SIDE_BOTTOM):
            segment = LineSegment.from_points(bottomLeft, bottomRight)    
        elif (sideName == Constants.TileConstants.SIDE_LEFT):
            segment = LineSegment.from_points(topLeft, bottomLeft)
        elif (sideName == Constants.TileConstants.SIDE_RIGHT):
            segment = LineSegment.from_points(topRight, bottomRight)
        else:
            raise NameError(sideName + ' is not a proper side name')
        
        return segment
    
    ############### PROPERTIES ###############
    
    def __get_name__(self):
        return self._name + ' ' + self.Position.__str__()
    
    Name = property(__get_name__, None, None, "Name of this GameTile and position in world coordinates.")