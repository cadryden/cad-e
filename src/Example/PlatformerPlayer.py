'''
Created on May 10, 2010

@author: Chris Alvarado-Dryden
'''
from Core import Constants

import os.path
import Utilities.HelperFunctions

from Core.Player import Player
from PlatformerActor import PlatformerActor
from Core.Animation import Animation
from Core.Sound import Sound

from PlatformerPlayerStates import *

class PlatformerPlayer(PlatformerActor, Player):
    '''
    classdocs
    '''

    def __init__(self, position, width, height, name, collisionGroupNames, transferName, playerNum, controller):
        '''
        Constructor
        '''
        
        # override width and height
        width = 30
        height = 94
        
        stateMappings = [('idle', IdleState(self)), ('run', RunState(self)), ('jump', JumpState(self)), ('fall', FallState(self)), ('land', LandState(self)), ('throw', ThrowState(self)), ('thrown', ThrownState(self)), ('dead', DeadState(self)), ('win', WinState(self)), ('lose', LoseState(self))]
        startStateName = 'fall'
        
        # respawn time for dead state
        self.respawnTime = 2.0
        self.RespawnPosition = position
        self.RespawnFacingRight = True
        
        image = None
        
        # player will be a box for now
        self.image = pygame.Surface((width, height))
        self.image = self.image.convert_alpha()
        
        self._color = Constants.GameObjectConstants.DEBUG_COLOR
        self.image.fill(self._color)
        
        # animation
        # list of tuples ('name', Animation, draw offset)
        
        sheetPath = os.path.normpath(os.path.realpath('../content/gfx/sprites/PlayerSheet' + str(playerNum+1) + '.png'))
        clearColor = None
        alpha = True
        
        # animations
        animationMappings = []
        animationMappings.append(('idle', Animation(sheetPath, pygame.Rect((0, 0, 45, 96)), 17, 4, -1, clearColor, alpha), Vector((-7, 0))))
        animationMappings.append(('run', Animation(sheetPath, pygame.Rect((0, 110, 100, 100)),  8, 1, -1, clearColor, alpha), Vector((-32, 0))))
        animationMappings.append(('launch', Animation(sheetPath, pygame.Rect((0, 218, 69, 94)), 1, 1, 1, clearColor, alpha), Vector((0, 0))))
        animationMappings.append(('jump', Animation(sheetPath, pygame.Rect((0, 321, 66, 107)), 2, 3, -1, clearColor, alpha), Vector((-18, 0))))
        animationMappings.append(('fall', Animation(sheetPath, pygame.Rect((0, 430, 81, 105)), 4, 3, -1, clearColor, alpha), Vector((-25, 0))))
        animationMappings.append(('land', Animation(sheetPath, pygame.Rect((0, 535, 76, 96)), 2, 1, 1, clearColor, alpha), Vector((-25, 0))))
        animationMappings.append(('throw', Animation(sheetPath, pygame.Rect((0, 632, 130, 102)), 4, 1, 3, clearColor, alpha), Vector((-50, 0))))
        animationMappings.append(('thrown', Animation(sheetPath, pygame.Rect((0, 735, 80, 95)), 5, 1, -1, clearColor, alpha), Vector((-24, 0))))
        animationMappings.append(('win', Animation(sheetPath, pygame.Rect((0, 828, 62, 110)), 4, 1, 3, clearColor, alpha), Vector((-15, -12))))
        animationMappings.append(('dead', Animation(sheetPath, pygame.Rect((0, 940, 105, 95)), 8, 1, 7, clearColor, alpha), Vector((-30, 10))))

        # sounds
        soundMappings = []
        #soundMappings.append(('throw', Sound('../resources/sounds/dp_finalfight.ogg', Constants.GameConstants.SOUND_VOLUME)))
        soundMappings.append(('hit', Sound('../content/sounds/hit.ogg', Constants.GameConstants.SOUND_VOLUME)))
        soundMappings.append(('jump', Sound('../content/sounds/jump.ogg', Constants.GameConstants.SOUND_VOLUME)))
        soundMappings.append(('swipe', Sound('../content/sounds/swipe.ogg', Constants.GameConstants.SOUND_VOLUME)))
        soundMappings.append(('land', Sound('../content/sounds/thud.ogg', Constants.GameConstants.SOUND_VOLUME)))
        soundMappings.append(('win', Sound('../content/sounds/win.ogg', Constants.GameConstants.SOUND_VOLUME)))
        #soundMappings.append(('count down', Sound('../resources/sounds/countdown.ogg', 0.1)))

        PlatformerActor.__init__(self, position, width, height, name, collisionGroupNames, transferName, stateMappings, startStateName, self.image, animationMappings, soundMappings)
        Player.__init__(self, position, width, height, name, collisionGroupNames, transferName, playerNum, controller, stateMappings, startStateName, self.image, animationMappings, soundMappings)

        # set some speeds for the player
        self._maxXVel = Constants.PlayerConstants.MAX_X_VELOCITY
        self._maxYVel = Constants.PlayerConstants.MAX_Y_VELOCITY
        self._maxFallVel = Constants.PlayerConstants.MAX_FALL_VELOCITY
        
        self._jumpVel = Constants.PlayerConstants.MAX_JUMP_VELOCITY
        self._runVel = Constants.PlayerConstants.MAX_RUN_VELOCITY        
        
        # to test map transfer
        self._numjumps = 0
        
        # test throw
        self.isThrowing = False
        self.isThrown = False
        throwBoxWidth = 48
        throwBoxHeight = 18
        self._throwBoxCenterOffset = Vector((32, -8))
        
        self.ThrowBox = pygame.Rect((self.boundingBox.centerx + self._throwBoxCenterOffset.x, self.boundingBox.centery + self._throwBoxCenterOffset.y), (throwBoxWidth, throwBoxHeight))  # throw hit box
        self.ThrowFrames = self._animations['throw'].LoopLength
        self.AirThrow = False
        
        self.ThrowVel = Vector((10000, 1000))
        self.ThrowVector = Vector((0, 0))
        self._throwCoolDown = 0
        
        # some goal variables
        self._win = False
        self._lose = False
        
        # restricted changes test
        self._restrictedStateTrans = [('dead', 'land'), ('dead', 'jump'), ('win', 'fall'), ('win', 'idle'), ('win', 'dead'), ('win', 'thrown'), ('lose', 'fall'), ('lose', 'idle'), ('lose', 'dead'), ('lose', 'thrown')]
        
        
        
        self._drawDebug = False
        
    def GetThrowCoolDown(self):
        return self._throwCoolDown
        
    def TransferFrom(self, other):
        self._numjumps = other._numjumps

    def Update(self, dt):
        
        self.__check_resolve_env_collisions__(self.Map.Layer('exit tiles'))
        
        PlatformerActor.Update(self, dt)
        
        if self._throwCoolDown > 0:
            self._throwCoolDown -= dt
            
        # update the throw hit box
        if self.FacingRight:
            self.ThrowBox.centerx = self.boundingBox.centerx + self._throwBoxCenterOffset.x
        else:
            self.ThrowBox.centerx = self.boundingBox.centerx - self._throwBoxCenterOffset.x
            
        self.ThrowBox.centery = self.boundingBox.centery + self._throwBoxCenterOffset.y
        
        
        otherPlayers = list(self.Map.Players) 
        otherPlayers.remove(self)
        
        # check against throwbox
        for other in otherPlayers:
            if self.isThrowing and not other.isThrown and self.ThrowBox.colliderect(other.boundingBox):
                other.ChangeState('thrown')
                other.Velocity = self.ThrowVector
                if self.ThrowVector.x > 0:
                    other.FacingLeft = True
                elif self.ThrowVector.x < 0:
                    other.FacingRight = True
            
            # make everyone else losers
            if self._currentState.Name == 'win':
                other.ChangeState('lose')
                    
                    
        if self.Controller.HasButton('Enable BBox') and self.Controller.Button('Enable BBox').Pressed:
            self._drawDebug = not self._drawDebug
            
    def ChangeState(self, stateName):
        
        if stateName == 'throw' and self._throwCoolDown > 0:
            return
        else:
            PlatformerActor.ChangeState(self, stateName)

    def ResolveCollision(self, other):
        """
        Resolves the collision between this Actor and the given GameObject.  This is a stub method and should be overridden
        by child classes.
        
        @type  other:    L{GameObject<GameObject.GameObject>}
        @param other:    GameObject this object is colliding with.
        """
        from Example.BounceTile import BounceTile
        from Example.ExitTile import ExitTile
        
        if isinstance(other, BounceTile):
            self.ChangeState('fall')
            # zero out Y then add bounce velocity
            self.Velocity = Vector((self.Velocity.x, other.BounceVelocity.y))
            
        elif isinstance(other, ExitTile) and not self.Lose:
            self.ChangeState('win')
            #self.Map.SwitchToMap(Constants.GameConstants.NEXT_MAP)
            
        """
        if isinstance(other, PlatformerPlayer):
            #self.Visible = not self.Visible # poops and gufaws - cad
            
            if self._currentState == self._stateMappings['throw'] and other._currentState != other._stateMappings['thrown']:
                other.ChangeState('thrown')
                other.Velocity = self.ThrowVector
                if self.ThrowVector.x >= 0:
                    other.FacingLeft = True
                else:
                    other.FacingRight = True
        """            
        return
        
    def Draw(self, cameras):
        
        PlatformerActor.Draw(self, cameras)
        
        
        if self._drawDebug:

            from Core.GameObject import GameObject
            
            #bounding box
            self.image = pygame.Surface((self.boundingBox.width, self.boundingBox.height))
            self.image = self.image.convert_alpha()
            self._color.a = 200
            self.image.fill(self._color)
            GameObject.Draw(self, cameras, [], True)
            
            
            #throw box
            
            self.image = pygame.Surface((self.ThrowBox.width, self.ThrowBox.height))
            bbox = self.boundingBox
            self.boundingBox = self.ThrowBox
            self.image = self.image.convert_alpha()
            self._color.a = 200
            self.image.fill(pygame.Color(200, 0, 200, 200))
            GameObject.Draw(self, cameras, [], True)
            
            # reset bounding/throw box
            self.boundingBox = bbox
            
        
    def __get_win__(self):
        return self._win
    def __set_win__(self, value):
        if value:
            self._win = True
            self._lose = False
        else:
            self._win = False
    
    def __get_lose__(self):
        return self._lose
    def __set_lose__(self, value):
        if value:
            self._lose = True
            self._win = False
        else:
            self._lose = False
            
    Win = property(__get_win__, __set_win__, None, "True if the player wins, False otherwise.")
    Lose = property(__get_lose__, __set_lose__, None, "True if the player loses, False otherwise.")