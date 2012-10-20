'''
Created on May 10, 2010

@author: Chris Alvarado-Dryden
'''

import pygame.rect
from Core import Constants

from Utilities.vector import Vector
from Core.Actor import Actor

class PlatformerActor(Actor):
    """
    @note: These Example docs aren't even started.
    
    @type _onGround:              C{bool}
    @ivar _onGround:              If the Actor is on the ground or in the air.
    
    @type _maxFallVel:            C{float}
    @ivar _maxFallVel:            The maximum number of pixels per second to fall.
    
    @type _runVel:        C{float}
    @ivar _runVel:        How many pixels per second to move when running.
    
    @type _jumpVel:       C{float}
    @ivar _jumpVel:       How many pixels per second to decrease the Y velocity (moving upward) when jumping.
    
    @type _facingRight:           C{bool}
    @ivar _facingRight:           C{True} if facing toward the right, C{False} otherwise.
    """


    def __init__(self, position, width, height, name, collisionGroupNames, transferName, stateMappings, startStateName, image=None, animationMappings=None, soundMappings=None):
        '''
        Constructor
        '''
        self._facingRight = True
        self._onGround = False
        
        # set some default max speeds
        self._maxXVel = Constants.PlayerConstants.MAX_X_VELOCITY
        self._maxYVel = Constants.PlayerConstants.MAX_Y_VELOCITY
        self._maxFallVel = Constants.PlayerConstants.MAX_FALL_VELOCITY
        
        self._jumpVel = Constants.PlayerConstants.MAX_JUMP_VELOCITY
        self._runVel = Constants.PlayerConstants.MAX_RUN_VELOCITY
        
        Actor.__init__(self, position, width, height, name, collisionGroupNames, transferName, stateMappings, startStateName, image, animationMappings, soundMappings)
        
        from Example.BounceTile import BounceTile
        from Example.ExitTile import ExitTile 
        from Example.KillTile import KillTile 
        self._specialTiles = [BounceTile, ExitTile, KillTile]
        
    def __update_position__(self, dt):
        """
        Based on the current L{Velocity<Actor.Actor.Velocity>} update L{Position<Actor.Actor.Position>}.  Gravity is
        also applied during this call.
        
        @type  dt:    C{float}
        @param dt:    Time in seconds since the last frame refresh.
        """    
        self.Velocity += (self.Map.gravity * dt)
        
        if self.Velocity.y > self._maxFallVel:
            self.Velocity = Vector((self.Velocity.x, self._maxFallVel))
        Actor.__update_position__(self, dt)
        
    def ResolveCollision(self, other):
        """
        Resolves the collision between this Actor and the given GameObject.  This is a stub method and should be overridden
        by child classes.
        
        @type  other:    L{GameObject<GameObject.GameObject>}
        @param other:    GameObject this object is colliding with.
        """
        from Example.BounceTile import BounceTile
        if isinstance(other, BounceTile):
            self.Velocity += other.BounceVelocity
        
        if isinstance(other, KillTile):
            pass
        
        if not isinstance(other, Actor):
            return
        
        #self.Visible = not self.Visible # poops and gufaws - cad

        if self.Velocity.length >= other.Velocity.length:
            self.Velocity = self.Velocity * -2
            self.ChangeState('fall')
                    
        return
        
    def __check_resolve_env_collisions__(self, collisionLayer):
        """
        Overriden to use our own collision resolution method.
        """
        previousBB = pygame.Rect(self._prevPosition, (self.boundingBox.width, self.boundingBox.height))
        
        # if we haven't moved, don't bother
        if (self.boundingBox.topleft == previousBB.topleft):
            return
        
        sideTiles, aboveBelowTiles = Actor.__get_colliding_tiles__(self, collisionLayer)
        
        # prioritize and resolve collisions if there are any
        # CAD - optimization breaks falling
        #if sideTiles or aboveBelowTiles:
        self.__resolve_tile_collisions__(sideTiles, aboveBelowTiles, previousBB, collisionLayer)

 
    def  __resolve_tile_collisions__(self, sideTiles, aboveBelowTiles, previousBB, collisionLayer):
        """
        Resolves collisions with Spike Tiles first, and sets State based on collision results.  These
        State changes would be appropriate for a platformer.
        """
        originalX, originalY = self.Position
        
        allTiles = set()
        allTiles.update(sideTiles)
        allTiles.update(aboveBelowTiles)
        
        for tile in allTiles:
            if type(tile) in self._specialTiles:
                self.ResolveCollision(tile)
                tile.ResolveCollision(self)
                
                # after resolving, get rid of all the tiles of that type so we only collide once
                for sideTile in list(sideTiles):
                    if isinstance(sideTile, type(tile)):
                        sideTiles.remove(sideTile)
                for aboveBelowTile in list(aboveBelowTiles):
                    if isinstance(aboveBelowTile, type(tile)):
                        aboveBelowTiles.remove(aboveBelowTile)
                break
        
        # collides with normal square tiles    
        if collisionLayer.Name == Constants.EditorConstants.LAYER_NAME_COLLISION_TILES:
            Actor.__resolve_tile_collisions__(self, sideTiles, aboveBelowTiles, previousBB, collisionLayer)
        
        # For a platformer, switch to the land state when hitting the ground
        if (originalY > self.Position[1]):
            # got pushed up, must be on ground 
            if not self._onGround:
                #self.ChangeState('land')
                self._onGround = True
        else:
            '''
            # little hack to make falling off things slower - CAD
            if (self._onGround):
                self.Velocity = Vector((self.Velocity.x, self.Velocity.y * 0.60))
            '''
            if (self.Velocity.y > 0.0):
                self._onGround = False
            
        if (originalY < self.Position[1]):
            # hit a ceiling, stop moving up
            self.Velocity = Vector((self.Velocity.x, 0))
        if (originalX != self.Position[0]):
            # hit a wall, Velocity goes to 0?
            self.Velocity = Vector((0, self.Velocity.y))
            
    def Draw(self, cameras, transformations=[], debug=False):
        # assume the sprite is facing to the right
        if self.FacingLeft:
            if not transformations:
                transformations = []
            func = pygame.transform.flip
            params = [True, False]
            transformations.append((func, params))
        Actor.Draw(self, cameras, transformations, debug)
    
    ############### PROPERTIES ###############
    
    def __get_facing_right__(self):
        """
        @rtype:    C{bool}
        """
        return self._facingRight
    def __set_facing_right__(self, isRight):
        """
        @type isRight:    C{bool}
        """
        self._facingRight = isRight    
    def __get_facing_left__(self):
        """
        @rtype:    C{bool}
        """
        return not self._facingRight
    def __set_facing_left__(self, isLeft):
        """
        @type isLeft:    C{bool}
        """
        self._facingRight = not isLeft
    
    def __get_onGround__(self):
        return self._onGround
    def __set_onGround__(self, value):
        self._onGround = value
    
    def __get_inAir__(self):
        return not self._onGround
    def __set_inAir__(self, value):
        self._onGround = not value
        
    def __get_runVel__(self):
        return self._runVel

    def __get_jumpVel__(self):
        return self._jumpVel
    
    FacingRight = property(__get_facing_right__, __set_facing_right__, None, "C{True} if facing toward the right.")
    FacingLeft = property(__get_facing_left__, __set_facing_left__, None, "C{True} if facing toward the left.")        
    OnGround = property(__get_onGround__, __set_onGround__, None, "C{True} if the Actor is touching ground, C{False} otherwise.")
    InAir = property(__get_inAir__, __set_inAir__, None, "C{True} if the Actor is in the air, C{False} otherwise.")
    RunVelocity = property(__get_runVel__, None, None, "The Player's velocity when running.")
    JumpVelocity = property(__get_jumpVel__, None, None, "The velocity applied to the Player when jumping.")