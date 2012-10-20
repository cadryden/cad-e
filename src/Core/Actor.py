'''
B{[Base Class]} A L{GameObject} with L{State<State.State>}.

@author: Chris Alvarado-Dryden
'''

import pygame
from Core import Constants
from Core.GameObject import GameObject
from Utilities.vector import Vector, LineSegment

class Actor(GameObject):
    """
    B{[Base Class]} An Actor is a L{GameObject} with L{State<State.State>}.  Unlike a standard GameObject, Actors are 
    free to L{move<Actor.Actor.__update_position__>} and L{collide with the environment<Actor.Actor.__check_resolve_env_collisions__>},
    depending on their current state.  To facilitate this, Actors include some properties to track movement
    (like L{Velocity<Actor.Actor.Velocity>}).
    
    Actors use states in two ways: as their primary state, and as effects.
    
        1.  B{Primary State}
            - This is the core logic of the Actor: how it behaves, how it processes input (if it takes input), and 
            its basic update.  For example, idle, running, jumping, and falling could all be different primary states, because
            each handles input and updates differently.
        2. B{Effects}
            - These additional states are applied on top of the primary state, and more than one can be active at a time.
            These are usually temporary (timed), and are a small modification to the Actor's behavior.  Examples include
            things like blinking, extra jump height, and faster run speed.  
    
    @see: For an example extension for a basic platformer, check out L{Example.PlatformerActor<Example.PlatformerActor.PlatformerActor>}
    and the other classes in the Example package.

    @type _map:                   L{GameMap<Map.GameMap.GameMap>}
    @ivar _map:                   The map the Actor is in.
    
    @type _velocity:              L{Vector<Utilties.vector.Vector>}
    @ivar _velocity:              Current velocity.
    
    @type _prevPosition:          L{Vector<Utilties.vector.Vector>}
    @ivar _prevPosition:          The Actor's position during the previous frame.
    
    @type _maxXVel:               C{float}
    @ivar _maxXVel:               The maximum number of pixels per second to move in the X direction. 
    
    @type _maxYVel:               C{float}
    @ivar _maxYVel:               The maximum number of pixels per second to move in the Y direction.
    
    @type _maxPixelsPerFrame:     C{int}
    @cvar _maxPixelsPerFrame:     The maximum number pixels the Actor is allowed to move per frame.
                                  It should be a little less than the tile size.
    
    @type _stateMappings:         C{dict}
    @ivar _stateMappings:         C{{str : L{State<States.State.State>}}} - Dictionary of State reference names to the States they refer to.
    
    @type _currentState:          L{State<States.State.State>}
    @cvar _currentState:          The current state this Actor is in.
    
    @type _effects:               C{list}
    @ivar _effects:               A list of L{State<State.State>}s that are temporarily affecting the Actor.
                                  Each will be applied in addition to the current state (primary state).
                                  
    @type cgroupNames:            C{list}
    @ivar cgroupNames:            A list of names for the L{CollisionGroup<CollisionGroup.CollisionGroup>}s
                                  this Actor should belong to.  Used when loading a map.
                                  
    @type _collisions:            C{set}
    @ivar _collisions:            A set of all other Map Objects which this Actor should check collisions against.
    
    @type _collisionGroups:       C{list}
    @ivar _collisionGroups:       A list of L{CollisionGroup<CollisionGroup.CollisionGroup>}s this Actor belongs to.
    
    @type _transferFromName:      C{str}
    @ivar _transferFromName:      Name of the Actor to transfer attributes from when switching between maps.
    
    @type  _restrictedStateTrans: C{list}
    @ivar  _restrictedStateTrans: List of tuples in the form C{(str, str)}.  The first string is the originating state name
                                  and the second is the target state name.  If the first state is trying to transition into
                                  the second it will be ignored.
    """
    
    _maxPixelsPerFrame = 30

    @staticmethod
    def PropertiesToParameters(properties):
        """
        Takes the values of the passed in dictionary and arranges them into an appropriate parameter list for object
        construction.  In addition to the U{Tiled<http://mapeditor.org/>} Properties, the dictionary will also include
        position, width, and height.
        
        For Actors, this will also include the names of L{CollisionGroup<CollisionGroup.CollisionGroup>}s (property
        I{collision groups}) the Actor should
        be a member of.
        
        @type  properties:    C{dict}
        @param properties:    C{{unicode : unicode}} - A dictionary of property names and their values.
        
        @rtype:               C{list}
        @return:              Values of the properties to be used as parameters, in parameter list order for the constructor.
        """
        params = GameObject.PropertiesToParameters(properties)
        
        # collision group names
        if (properties.has_key(Constants.EditorConstants.OBJ_ACTOR_PROP_COLLISION_GROUPS) and properties[Constants.EditorConstants.OBJ_ACTOR_PROP_COLLISION_GROUPS].strip()):
            cgroupNames = properties[Constants.EditorConstants.OBJ_ACTOR_PROP_COLLISION_GROUPS]
            cgroupNames = map(unicode.strip, cgroupNames.split(','))
        else:
            cgroupNames = []
        
        if(properties.has_key(Constants.EditorConstants.OBJ_ACTOR_PROP_TRANSFER_NAME) and properties[Constants.EditorConstants.OBJ_ACTOR_PROP_TRANSFER_NAME].strip()):
            transferName = properties[Constants.EditorConstants.OBJ_ACTOR_PROP_TRANSFER_NAME]
        else:
            transferName = ''
        
        params.append(cgroupNames)
        params.append(transferName)
        
        return params

    def __init__(self, position, width, height, name, collisionGroupNames, transferName, stateMappings, startStateName, image=None, animationMappings=None, soundMappings=None, stateTransitionRestrictions=None):
        """
        Creates a new Actor.  Initializes all Actor variables, but should be extended by derived classes.
        
        @type  position:             C{(int, int)} | L{Vector<Utilities.vector.Vector>}
        @param position:             World coordinates of the top left corner of the object's bounding box.
        
        @type  width:                C{int}
        @param width:                Width of the object's bounding box in pixels.
        
        @type  height:               C{int}
        @param height:               Height of the object's bounding box in pixels.
        
        @type  name:                 C{str}
        @param name:                 Name for this Actor.
        
        @type  collisionGroupNames:  C{list}
        @param collisionGroupNames:  List of names (C{str}) of L{CollisionGroup<CollisionGroup.CollisionGroup>}s that
                                     this Actor should be part of.
                                     
        @type  transferName:         C{str}
        @param transferName:         Name of the Actor to transfer attributes from when switching between maps. 
        
        @type  stateMappings:        C{list}
        @param stateMappings:        List of pairs in the form C{str, L{State<State.State>}} which are the States available to
                                     this Actor.  In detail they are:
                                         - C{str} - Name to use to refer to this State.
                                         - C{State} - The State object.
        
        @type  startStateName:       C{str}
        @param startStateName:       Name of the L{State<State.State>} the Actor will start in.
        
        @type  image:                U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
        @param image:                Static image that should be drawn at the object's L{Position}.
        
        @type  animationMappings:    C{list}
        @param animationMappings:    List of tuples in the form C{(str, L{Animation<Animation.Animation>}, (int, int))}.
                                     In detail they are:
                                         - C{str} - Name to use to refer to this Animation.
                                         - C{Animation} - Animation object itself.
                                         - C{(int, int)} - Offset from the GameObject's L{Position} where the top-left of the Animation's frames
                                         should be drawn.

        @type  soundMappings:        C{list}
        @param soundMappings:        List of tuples in the form C{(str, L{Sound<Sound.Sound>})}.
                                     In detail they are:
                                         - C{str} - Name to use to refer to this Sound.
                                         - C{Sound} - Sound object itself.
                                         
                                         
        @type  stateTransitionRestrictions:    C{list}
        @param stateTransitionRestrictions:    List of tuples in the form C{(str, str)}.  The first string is the originating state name
                                               and the second is the target state name.  If the first state is trying to transition into
                                               the second it will be ignored.
        """
        GameObject.__init__(self, position, width, height, None, name, image, animationMappings, soundMappings)
        
        # collision groups
        self.cgroupNames = collisionGroupNames
        self._collisionGroups = []
        self._collisions = set()
        
        # states
        self._stateMappings = {}
        for name, state in stateMappings:
            self._stateMappings[name] = state
        
        # state restrictions
        self._restrictedStateTrans = []
        if self._restrictedStateTrans:
            for statePair in stateTransitionRestrictions:
                self._restrictedStateTrans.append(statePair)
        
        # velocities are in pixels/second
        self._velocity = Vector((0, 0))
        self._prevPosition = Vector(self.Position)
        
        # some maximum values
        self._maxXVel = Constants.ActorConstants.MAX_X_VELOCITY
        self._maxYVel = Constants.ActorConstants.MAX_Y_VELOCITY
        
        # make sure the state is setup correctly
        self._currentState = self._stateMappings[startStateName]
        self._currentState.OnEnter()
        
        # effects
        self._effects = []
        
        # map transition
        self._transferFromName = transferName
        
    def TransferFrom(self, other):
        """
        B{[Stub]} Initializes some of this Actors attributes with those of the given Actor.  This function is called when changing
        between L{GameMap<Map.GameMap.GameMap>}s and Actor data should be carried over.
        
        This is a stub and should be overridden by child classes.
        
        @type  other:        C{Actor}
        @param other:        Actor whose attributes to use.
        """
        return
        
    def Update(self, dt):
        """
        Update logic for the Actor based on its current L{State<States.State.State>} and effects, and check non-tile
        collisions.
        
        @type  dt:    C{float}
        @param dt:    Time in seconds since the last frame refresh.
        """
        self._prevPosition = self.Position
        
        for effect in self._effects:
            effect.Update(dt)
        
        self.__check_collision_groups__()
        
        self._currentState.Update(dt)

    def __check_collision_groups__(self):
        """
        Checks collisions between this Actor and every other object in its L{CollisionGroup<CollisionGroup.CollisionGroup>}s.
        To prevent redundant checks, when Actor A checks against B, the check between B and A is removed. 
        """
        # if we don't have any collisions, get some
        if len(self._collisions) == 0:
            self.__refresh_collision_set__()
        
        # don't need to check against ourselves
        self.__remove_collision__(self)
        
        for collidable in self._collisions:
            
            # if the other object doesn't have a collision set, get one
            # this is OK because the other object will keep this set until it updates and removes itself
            if (len(collidable._collisions) == 0):
                collidable.__refresh_collision_set__()
            
            # resolve collisions
            if self.Collides(collidable):
                self.ResolveCollision(collidable)    
                collidable.ResolveCollision(self)
            
            # remove from the other object's collision list, so it doesn't have to do the same check
            collidable.__remove_collision__(self)
        
        # finished checking collisions, so clear the collision set
        self._collisions.clear()
        
    def __refresh_collision_set__(self):
        """
        Gets a fresh set of all Actors this Actor should check collisions against.  That is all members of the
        L{CollisionGroup<CollisionGroup.CollisionGroup>}s this Actor's collision groups collide with.  This should be
        once per collision check cycle (usually once per frame).
        """
        self._collisions.clear()
        for group in self.CollisionGroups:
            self._collisions.update(group.CollidableSet())
        
    
    def __remove_collisions__(self, collisionSet):
        """
        Remove the given collisions from this frame's collision set.
        
        @type  collisionSet:    C{set}
        @param collisionSet:    The collisions that shouldn't be checked this frame.
        """
        self._collisions.difference_update(collisionSet)
        
    def __remove_collision__(self, collidable):
        """
        Remove the given collision from this frame's collision set.
        
        @type  collidable:    C{Actor}
        @param collidable:    The collision that shouldn't be checked this frame.
        """
        self._collisions.discard(collidable)
    
    def __update_position__(self, dt):
        """
        Based on the current L{Velocity<Actor.Actor.Velocity>} update L{Position<Actor.Actor.Position>}.
        
        @type  dt:    C{float}
        @param dt:    Time in seconds since the last frame refresh.
        """
        
        if abs(self.Velocity.x) > self._maxXVel:
            self.Velocity = Vector((self._maxXVel * (self.Velocity.x / abs(self.Velocity.x)), self.Velocity.y))                  
        if abs(self.Velocity.y) > self._maxYVel:
            self.Velocity = Vector((self.Velocity.x, self._maxYVel * (self.Velocity.y / abs(self.Velocity.y))))
        
        distance = self.Velocity * dt
        
        # moving at 1300 pixels/second or higher, this hack comes into play
        if (abs(distance.x) >= self._maxPixelsPerFrame):
            distance = Vector(((self._maxPixelsPerFrame - 1) * (distance.x / abs(distance.x)), distance.y))
        if (abs(distance.y) >= self._maxPixelsPerFrame):
            distance = Vector((distance.x, (self._maxPixelsPerFrame - 1) * (distance.y / abs(distance.y))))

        self.Position += distance
    
    def __get_colliding_tiles__(self, collisionLayer):
        """
        Gets L{GameTile<Map.GameTile.GameTile>}s that are colliding with the edges of the Actor's bounding box.
        Depending on the direction the Actor is moving, only two sides will be checked.  Either the top or bottom
        side, if the Actor is moving up or down, and likewise the left or right side if the Actor is moving left or right.
        
        Corner tiles will also be removed from the lists I{if and only} if they colliding with both the side and top/bottom.
        This eliminates the literal corner case of diagonally colliding with a tile the Actor shouldn't be able to reach.
        
        @type  collisionLayer:    L{GameTileLayer<Map.GameTileLayer.GameTileLayer>}
        @param collisionLayer:    Layer whose tiles to use for collision detection.
        
        @rtype:                   C{(list, list)}
        @return:                  L{GameTile<Map.GameTile.GameTile>}s colliding on the left or right, and
                                  tiles colliding above or below.
        """

        sideTiles = []
        if self.Velocity.x > 0:
            sideTiles = collisionLayer.TilesBetweenCoords(self.boundingBox.topright, self.boundingBox.bottomright)
        elif self.Velocity.x < 0:
            sideTiles = collisionLayer.TilesBetweenCoords(self.boundingBox.topleft, self.boundingBox.bottomleft)
        
        aboveBelowTiles = []
        if self.Velocity.y > 0:
            aboveBelowTiles = collisionLayer.TilesBetweenCoords(self.boundingBox.bottomleft, self.boundingBox.bottomright)
        elif self.Velocity.y < 0:
            aboveBelowTiles = collisionLayer.TilesBetweenCoords(self.boundingBox.topleft, self.boundingBox.topright)
        
        # remove extra tiles that we won't actually reach
        if len(sideTiles) > 1:
            for tile in sideTiles:
                if tile in aboveBelowTiles:
                    sideTiles.remove(tile)
                    aboveBelowTiles.remove(tile)
        if len(aboveBelowTiles) > 1:
            for tile in aboveBelowTiles:
                if tile in sideTiles:
                    sideTiles.remove(tile)
                    aboveBelowTiles.remove(tile)
        
        return (sideTiles, aboveBelowTiles)
    
    def __check_resolve_env_collisions__(self, collisionLayer):
        """
        Default tile collision check and resolution method.  Finds colliding tiles and resolves the collisions.
        This method should be overridden in child classes if non-default checks or resolutions are required.
        
        @type  collisionLayer:    L{GameTileLayer<Map.GameTileLayer.GameTileLayer>}
        @param collisionLayer:    Layer whose tiles to use for collision detection.
        """
        previousBB = pygame.Rect(self._prevPosition, (self.boundingBox.width, self.boundingBox.height))
        
        # if we haven't moved, don't bother
        if (self.boundingBox.topleft == previousBB.topleft):
            return

        sideTiles, aboveBelowTiles = self.__get_colliding_tiles__(collisionLayer)
                
        # prioritize and resolve collisions if there are any
        #CAD - in or out?
        #if sideTiles or aboveBelowTiles:
        self.__resolve_tile_collisions__(sideTiles, aboveBelowTiles, previousBB, collisionLayer)
       
    def __resolve_tile_collisions__(self, sideTiles, aboveBelowTiles, previousBB, collisionLayer):
        """
        Default tile collision resolution method.  Moves the Actor outside of the given tiles.  This method should
        be extended in child classes if non-default resolutions are required.
        
        @type  sideTiles:          C{list}
        @param sideTiles:          L{GameTile<Map.GameTile.GameTile>}s colliding with either the right or left
                                   side of the Actor's bounding box.
        
        @type  aboveBelowTiles:    C{list}
        @param aboveBelowTiles:    L{GameTile<Map.GameTile.GameTile>}s colliding with either the top or bottom
                                   side of the Actor's bounding box.
        
        @type  previousBB:         C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param previousBB:         Bounding box at the previous position.
        """
        
        # use whatever tiles we have for regular collision detection
        originalX, originalY  = self.Position
        
        from decimal import Decimal
               
        newX, minX = map(Decimal, map(str, self.__calc_x_collision_adjustment__(sideTiles, previousBB)))
        newY, minY = map(Decimal, map(str, self.__calc_y_collision_adjustment__(aboveBelowTiles, previousBB)))
        
        if ((minX < minY and minX != -1) or (minX >= 0.0 and minY == -1)):
            # X collision occurred sooner
            self.Position = (newX, self.Position[1])
            
            # get Y with the new bounding box
            # and re-get colliding tiles with new bounding box
            newY = self.__calc_y_collision_adjustment__(self.__get_colliding_tiles__(collisionLayer)[1], previousBB)[0]
            
            self.Position = (self.Position[0], newY)
            
        elif ((minY < minX and minY != -1) or (minY >= 0.0 and minX == -1)):
            # Y collision occurred sooner
            self.Position = (self.Position[0], newY)
            
            # get X with the new bounding box
            # and re-get colliding tiles with new bounding box
            newX = self.__calc_x_collision_adjustment__(self.__get_colliding_tiles__(collisionLayer)[0], previousBB)[0]
            
            self.Position = (newX, self.Position[1])    
        else:
            # they're equal, see which frees the actor first, otherwise do both
            self.Position = (newX, originalY)
            
            if (originalY != self.__calc_y_collision_adjustment__(aboveBelowTiles, previousBB)[0]):
                # x movement didn't clear, reset and try Y
                self.Position = (originalX, newY)
                
                if (originalX != self.__calc_x_collision_adjustment__(sideTiles, previousBB)[0]):
                    # y movement didn't clear either, do both
                    self.Position = (newX, newY)
    
    def __calc_y_collision_adjustment__(self, tiles, previousBB):
        """
        Suggests a new Y coordinate for the Actor's bounding box outside of the given colliding tiles.
        Checks tiles above and below the Actor and finds the closest Y coordinate that clears the bounding tiles.
        
        Coordinates are always adjusted in the direction of the Actor's previous position. 
        
        @type  tiles:             C{list}
        @param tiles:             L{GameTile<Map.GameTile.GameTile>}s colliding with either the top or bottom
                                  side of the Actor's bounding box.
        
        @type  previousBB:        C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param previousBB:        Bounding box at the previous position.
        
        @rtype:                   C{(int, int)}
        @return:                  Suggested new Y position and how close the intersection was to the previous position (-1 means no
                                  intersection occurred).
        """
        
        moveTo = self.Position[1]
        minDistance = -1
        
        if not tiles:
            return moveTo, minDistance
        
        yVel = self.Velocity.y
        
        # a tile
        tile = tiles[0]
        
        # amount to move the boundary to avoid a false negative intersection 
        bumpAmount = 0.0001
        
        # get the tile segment above or below
        if (yVel > 0):
            # going down
            tileSeg = tile.GetSegment(Constants.TileConstants.SIDE_TOP)
            # prepare to create segments from our side at the old position to the side at the new position            
            prevSide = LineSegment.from_points(previousBB.bottomleft, previousBB.bottomright)
            if self.boundingBox.bottom == tileSeg.start.y:
                curSide = LineSegment.from_points((self.boundingBox.left, self.boundingBox.bottom + bumpAmount), (self.boundingBox.right, self.boundingBox.bottom + bumpAmount))
            else:
                curSide = LineSegment.from_points(self.boundingBox.bottomleft, self.boundingBox.bottomright)
        elif (yVel < 0):
            # going up
            tileSeg = tile.GetSegment(Constants.TileConstants.SIDE_BOTTOM)
            # prepare to create segments from our side at the old position to the side at the new position
            prevSide = LineSegment.from_points(previousBB.topleft, previousBB.topright)
            if self.boundingBox.top == tileSeg.start.y:
                curSide = LineSegment.from_points((self.boundingBox.left, self.boundingBox.top - bumpAmount), (self.boundingBox.right, self.boundingBox.top - bumpAmount))
            else:
                curSide = LineSegment.from_points(self.boundingBox.topleft, self.boundingBox.topright)
        else:
            # suggest no movement if we aren't going anywhere
            return moveTo, minDistance
            
        tileSegStart = (min(self.boundingBox.left, previousBB.left), tileSeg.start.y)
        tileSegEnd = (max(self.boundingBox.right, previousBB.right), tileSeg.end.y)
        
        tileSeg = LineSegment.from_points(tileSegStart, tileSegEnd)
        bbSeg = LineSegment.from_points(prevSide.mid, curSide.mid)
        
        intersect, point = bbSeg.intersects(tileSeg)          
        
        if (intersect):
            if (bbSeg.start == point):
                distance = 0
                moveTo = point[1]
            else:
                distance = LineSegment.from_points(bbSeg.start, point).length
                
            if distance == 0:
                for t in tiles:
                    # if the point is inside the borders of the segment, set up the move
                    # this is <= to prioritize vertical checks slightly over horizontal checks to prevent "catching" on some corners
                    if (t.boundingBox.left >= previousBB.left and t.boundingBox.left <= t.boundingBox.right) or (t.boundingBox.right >= previousBB.left and t.boundingBox.right <= previousBB.right):
                        minDistance = distance
                        moveTo = point[1]
                        break
                    
                    # otherwise it's -1 and we don't move    
                    minDistance = -1
                    moveTo = self.Position[1]
                    
            else:
                minDistance = distance
                moveTo = point[1]
        
        if (moveTo != self.Position[1] and self.Velocity.y > 0):
            # going down, add our height
            moveTo -= self.Height + 1
        
        return moveTo, minDistance
    
    def __calc_x_collision_adjustment__(self, tiles, previousBB):
        """
        Suggests a new X coordinate for the Actor's bounding box outside of the given colliding tiles.
        Checks tiles to the left and right of the Actor and finds the closest X coordinate that clears the bounding tiles.
        
        Coordinates are always adjusted in the direction of the Actor's previous position.  
        
        @type  tiles:             C{list}
        @param tiles:             L{GameTile<Map.GameTile.GameTile>}s colliding with either the left or right
                                  side of the Actor's bounding box.
        
        @type  previousBB:        C{U{pygame.Rect<http://www.pygame.org/docs/ref/rect.html>}}
        @param previousBB:        Bounding box at the previous position.

        @rtype:                   C{(int, int)}
        @return:                  Suggested new X position and how close the intersection was to the previous position (-1 means
                                  no collision occurred).
        """
        
        moveTo = self.Position[0]
        minDistance = -1
        
        if not tiles:
            return moveTo, minDistance
        
        xVel = self.Velocity.x
        
        # a tile
        tile = tiles[0]
        
        # amount to move the boundary to avoid a false negative intersection 
        bumpAmount = 0.0001
        
        # get the tiles to the left or right
        if (xVel > 0):
            # going right
            tileSeg = tile.GetSegment(Constants.TileConstants.SIDE_LEFT)
            # prepare to create segments from our side at the old position to the side at the new position
            prevSide = LineSegment.from_points(previousBB.topright, previousBB.bottomright)
            if self.boundingBox.right == tileSeg.start.x:
                curSide = curSide = LineSegment.from_points((self.boundingBox.right + bumpAmount, self.boundingBox.top), (self.boundingBox.right + bumpAmount, self.boundingBox.bottom))
            else:
                curSide = LineSegment.from_points(self.boundingBox.topright, self.boundingBox.bottomright)
        elif (xVel < 0):
            # going left
            tileSeg = tile.GetSegment(Constants.TileConstants.SIDE_RIGHT)
            # prepare to create segments from our side at the old position to the side at the new position
            prevSide = LineSegment.from_points(previousBB.topleft, previousBB.bottomleft)
            if self.boundingBox.left == tileSeg.start.x:
                curSide = LineSegment.from_points((self.boundingBox.left - bumpAmount, self.boundingBox.top), (self.boundingBox.left - bumpAmount, self.boundingBox.bottom))
            else:
                curSide = LineSegment.from_points(self.boundingBox.topleft, self.boundingBox.bottomleft)
        else:
            # suggest no movement if we aren't going anywhere
            return moveTo, minDistance

        tileSegStart = (tileSeg.start.x, min(self.boundingBox.top, previousBB.top))
        tileSegEnd = (tileSeg.end.x, max(self.boundingBox.bottom, previousBB.bottom))
        
        tileSeg = LineSegment.from_points(tileSegStart, tileSegEnd)
        bbSeg = LineSegment.from_points(prevSide.mid, curSide.mid)
        
        intersect, point = bbSeg.intersects(tileSeg)
        
        if (intersect):
            if (bbSeg.start == point):
                distance = 0
                moveTo = point[0]
            else:
                distance = LineSegment.from_points(bbSeg.start, point).length
            
            if distance == 0:
                for t in tiles:
                    # if the point is inside the borders of the segment, set up the move
                    # this is < to prioritize horizontal checks slightly below vertical checks to prevent "catching" on some corners
                    if (t.boundingBox.top > previousBB.top and t.boundingBox.top < t.boundingBox.bottom) or (t.boundingBox.bottom > previousBB.top and t.boundingBox.bottom < previousBB.bottom):
                        minDistance = distance
                        moveTo = point[0]
                        break
                    
                    #otherwise we don't move
                    minDistance = -1
                    moveTo = self.Position[0]
                        
            else:
                minDistance = distance
                moveTo = point[0]        
        
        if (moveTo != self.Position[0]):
            if(xVel > 0):
                # going right, add our width
                moveTo -= self.Width + 1
            elif (xVel < 0):
                # going left, a little bump over
                moveTo += 1
        
        return moveTo, minDistance
           
    def __add_state__(self, state, stateName):
        """
        Makes the given L{State<States.State.State>} available this Actor.
        
        @type  state:             L{State<States.State.State>}
        @param state:             State to make available to this Actor.
        
        @type  stateName:         C{str}
        @param stateName:         Name this Actor will use to refer to this State.
        """
        self._stateMappings[stateName] = state
    
    def __remove_state__(self, stateName):
        """
        Removes the state L{State<States.State.State>} referred to by the given name from this Actor.
        
        @type  stateName:         C{str}
        @param stateName:         Name of the State to remove.
        """
        self._stateMappings.pop(stateName)
    
    def ChangeState(self, stateName):
        """
        Changes the current L{State<States.State.State>} to the one with the given name.  When changing, the old state's 
        L{State.OnExit<States.State.State.OnExit>} is called, and the new state's L{State.OnEnter<States.State.State.OnEnter>}
        is called.
        
        An Actor cannot change into the same state it is already in, and will not change through a restricted transition (todo CAD LINK).
        
        @type  stateName:        C{str}
        @param stateName:        Actor's name for the state to change to.
        """
        # don't re-enter the same state
        if (self._currentState is self._stateMappings[stateName]):
            return
        
        # don't enter a restricted state
        for fromState, toState in self._restrictedStateTrans:
            if self._currentState.Name == fromState and stateName == toState:
                return
        
        newState = self._stateMappings[stateName]
        
        #print 'Actor type: ', type(self), ' Changing state from: ', self._currentState.Name, ' to: ', newState.Name

        self._currentState.OnExit()
        self._currentState = newState
        self._currentState.OnEnter()
        
    def ApplyEffect(self, effect):
        """
        Adds the given effect to this Actor's list of effects and begins it.
        
        @type  effect:        L{State<State.State>}
        @param effect:        The effect to add to this Actor's effects.
        """
        self._effects.append(effect)
        effect.OnEnter()
        
    def RemoveEffect(self, effect):
        """
        Removes the given effect from this Actor's list of effects and ends it.
        
        @type  effect:        L{State<State.State>}
        @param effect:        The effect to remove from this Actor's effects.
        """
        if (not effect in self._effects):
            raise Exception('Effect ' + effect.Man + effect.__str__() + ' is not on this Actor' + self.__str__())
        effect.OnExit()
        self._effects.remove(effect)
        
    def RemoveEffectsNamed(self, effectName):
        """
        Removes all effects with the given name from this Actor.
        
        @type  effectName:    C{str}
        @param effectName:    The name of the effect(s) to remove.
        """
        found = False
        for effect in list(self._effects):
            if (effect.Name == effectName):
                self.RemoveEffect(effect)
                found = True
        
        if not found:
            raise Exception('No events named ' + effectName + ' found on this Actor' + self.__str__())

    ############### PROPERTIES ###############
       
    def __get_velocity__(self):
        return self._velocity
    def __set_velocity__(self, value):
        if (not isinstance(value, Vector)):
            value = Vector(value)
        self._velocity = value
    
    def __get_collisionGroups__(self):
        return self._collisionGroups
        
    def __get_map__(self):
        return self._map
    def __set_map__(self, value):
        self._map = value
        
    def __get_layer__(self):
        return self._layer
    def __set_layer__(self, value):
        self._layer = value
        
    def __get_current_state__(self):
        return self._currentState
        
    Velocity = property(__get_velocity__, __set_velocity__, None, "The Actor's current velocity in pixels/second.")
    CollisionGroups = property(__get_collisionGroups__, None, None, "The L{CollisionGroup<CollisionGroup.CollisionGroup>}s this Actor belongs to.")
    Map = property(__get_map__, __set_map__, None, "The L{GameMap<Map.GameMap.GameMap>} this Actor is in.")
    Layer = property(__get_layer__, __set_layer__, None, "The L{GameObjectlayer<Map.GameObjectLayer.GameObjectLayer>} this Actor is on.")
    CurrentState = property(__get_current_state__, None, "The current L{State<States.State.State>} this Actor is in.")