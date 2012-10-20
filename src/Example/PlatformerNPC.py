'''
Created on Mar 24, 2010

@author: Chris Alvarado-Dryden
'''

import pygame
from Core import Constants
from PlatformerActor import PlatformerActor
from States.State import State
from Core.Animation import Animation
from Utilities.vector import Vector

class PlatformerNPC(PlatformerActor):
    """
    A test/example L{Actor<Actor.Actor>}.
    
    This actor does nothing but stand in place (it can fall too).  It demonstrates the basic L{State<States.State.State>} actors should
    have (idle, fall, land).  Additionally, it has the L{BlinkEffect} applied when it is created.
    """
    
    def __init__(self, position, width=20, height=30, name='', collisionGroupNames=None, transferName='', image=None):
        """
        Standard constructor takes in position and can override width and height.
        
        @type  position: C{(int, int)} or L{Vector<Utilities.vector.Vector>}
        @param position: The world coordinates of the top left corner of the object's bounding box
        
        @type  width:    C{int}
        @param width:    The width of the object's bounding box in pixels.
        
        @type  height:   C{int}
        @param height:   The height of the object's bounding box in pixels.
        
        @type  collisionGroupNames:  C{list}
        @param collisionGroupNames:  List of names (C{str}) of L{CollisionGroup<CollisionGroup.CollisionGroup>} that
                                     this Actor should be part of.
        
        @type  image:    U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
        @param image:    The static image that should be drawn at the object's L{Position}
        """
        # animation
        # list of tuples ('name', Animation, draw offset)
        animationMappings = []
        animationMappings.append(('idle', Animation('../content/gfx/sprites/HulkGreen.png', pygame.Rect((0, 0, 160, 124)), 8, 3, -1, pygame.Color(49, 115, 255)), Vector((-60, -80))))
        animationMappings.append(('fall', Animation('../content/gfx/sprites/HulkGreen.png', pygame.Rect((0, 247, 130, 225)), 2, 3, -1, pygame.Color(49, 115, 255)), Vector((-54, -180))))
        animationMappings.append(('land', Animation('../content/gfx/sprites/HulkGreen.png', pygame.Rect((0, 127, 140, 120)), 4, 3, 3, pygame.Color(49, 115, 255)), Vector((-54, -80 + 4))))
        
        self.color = pygame.Color(0, 0, 0)
        
        PlatformerActor.__init__(self, position, width, height, name, collisionGroupNames, transferName, [('idle', NPCIdle(self)), ('fall', NPCFall(self)), ('land', NPCLand(self))], 'fall', image, animationMappings)
        
        
        # blink
        self.ApplyEffect(BlinkEffect(self, 1.0, 0.25))
 
 
        
    def Draw(self, cameras):
        """
        Standard draw, sending the image to the cameras for drawing.
        
        @type cameras:    C{list}
        @param cameras:   The list of L{Camera} objects that should try to be drawn to.
        """
        # draw animation
        PlatformerActor.Draw(self, cameras)
        
        # then the bounding box with state colors
        self._drawPoint = None
        self.image = pygame.Surface((self.boundingBox.width, self.boundingBox.height))
        self.image = self.image.convert_alpha()
        self.image.fill(self.color)
        
        from Core.GameObject import GameObject
        GameObject.Draw(self, cameras, [], True)


########### Baseline example States ########### 
    
class NPCLand(State):
    """
    A test/example landing state.  Used to transition from a L{fall<NPCFall>} state to L{idle<NPCIdle>}.
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'land')
        
    def OnEnter(self):
        """
        Ensure the Actor is on the ground.
        """
        self._owner.PlayAnimation('land')
        self._owner.ChangeState('idle')
        
        self._owner.QueueAnimation('idle')
        self._owner._onGround = True 

class NPCIdle(State):
    """
    A test/example idle state.
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'idle')
        
    def OnEnter(self):
        """
        Ensure the Actor is on the ground.
        """
        self._owner.color = pygame.Color(255, 255, 0, 100)
        self._owner._onGround = True
        
        #self._owner.PlayAnimation('idle') # test
        
    def Update(self, dt):
        """
        Keep detecting collisions.
        """
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.InAir:
            self._owner.ChangeState('fall')
        #self._owner.__resolve_env_collisions__(self._owner.Map.Layer(0))
        
class NPCFall(State):
    """
    A test/example fall state.  Transitions to the L{land<NPCLand>} state.
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'fall')
        
    def OnEnter(self):
        """
        Ensure the Actor is in the air.
        """
        self._owner.color = pygame.Color(0, 255, 255, 100)
        self._owner._onGround = False
        
        self._owner.PlayAnimation('fall') # TEST 
        
    def Update(self, dt):
        """
        Keep detecting collisions.
        """
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.OnGround:
            self._owner.ChangeState('land')
        #self._owner.__resolve_env_collisions__(self._owner.Map.Layer(0))
        

################## An Effect! ##################         
        
class BlinkEffect(State):
    """
    An example effect that causes the Actor to blink for a certain amount of time.
    
    @type _expireTime:        C{float}
    @ivar _expireTime:        How long the effect should last, in seconds.
    
    @type _timeLeft:          C{float}
    @ivar _timeLeft:          Time left, in seconds, before the effect expires.
    
    @type _halfFrequency:     C{float}
    @ivar _halfFrequency:     Half of the frequency of a blink cycle.
    
    @type _timeLeftVisible:   C{float}
    @ivar _timeLeftVisible:   Time left, in seconds, before the Actor switches between visible and not visible.
    
    
    """
    def __init__(self, owner, time=5.0, frequency=0.25):
        """
        Creates the effect that will last for the given time, and blink at the given frequency.
        
        @type  owner:        L{Actor<Actor.Actor>}
        @param owner:        Who this State belongs to.
        
        @type  time:         C{float}
        @param time:         How many seconds the effect should last.
        
        @type  frequency:    C{float}
        @param frequency:    Length in seconds of a single on and off cycle. 
        """
        State.__init__(self, owner, 'blink')
        self._expireTime = time
        self._halfFrequency = frequency / 2.0
        
        self._timeLeft = self._expireTime
        self._timeLeftVisible = self._halfFrequency
        
    def OnEnter(self):
        """
        Begin blinking.
        """
        self._owner.Visible = True
        self._timeLeft = self._expireTime
        self._timeLeftVisible = self._halfFrequency
        
    def Update(self, dt):
        """
        Continue blinking and keeping track of the time.
        """
        self._timeLeft -= dt
        self._timeLeftVisible -= dt
        
        if (self._timeLeftVisible <= 0.0):
            self._owner.Visible = not self._owner.Visible
            self._timeLeftVisible = self._halfFrequency
            
        if (self._timeLeft <= 0.0):
            self._owner.RemoveEffect(self)
            
    def OnExit(self):
        """
        Make sure the Actor is visible when the effect is over.
        """
        self._owner.Visible = True
