'''
Created on May 12, 2010

@author: Chris Alvarado-Dryden
'''

import pygame
from Core import Constants
from Utilities.vector import Vector
from States.State import State
from States.PlayerState import PlayerState

######### FALL #########

class FallState(PlayerState):
    """
    L{Player<Player.Player>} state for falling.  Triggered after the apex of a jump, or when no longer colliding with the ground.
    From a here, a Player will enter the L{LandState<LandState.LandState>}.
    """
    def __init__(self, owner):
        State.__init__(self, owner, Constants.StateConstants.FALL_NAME)
        
    def OnEnter(self):
        """
        Forces the player to be in the air.
        """
        self._owner._color = pygame.Color(0, 0, 150)
        self._owner.InAir = True
        self._owner.PlayAnimation('fall')
        
    def Update(self, dt):
        """
        Process input, move the Player, and check for collisions.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.OnGround:
            self._owner.ChangeState('land')
            
        self._owner.CurrentState.ProcessInput()
        
    def ProcessInput(self):
        """
        Processes the L{Player.Controller} input.  Right and left move the player through the air.
        """
        controller = self._owner.Controller
        
        if (controller.dpad.Right.Down):
            self._owner.Velocity = Vector((self._owner.RunVelocity, self._owner.Velocity.y))
        elif (controller.dpad.Left.Down):
            self._owner.Velocity = Vector((-self._owner.RunVelocity, self._owner.Velocity.y))
        else:
            self._owner.Velocity = Vector((0, self._owner.Velocity.y))
            
        if(controller.Button('Throw').Pressed and not self._owner.AirThrow):
            self._owner.ChangeState('throw')
            
######### IDLE #########
            
class IdleState(PlayerState):
    """
    State for when the L{Player<Player.Player>} is not moving.
    From here, a Player can enter the L{RunState<RunState.RunState>}, L{JumpState<JumpState.JumpState>},
    or L{FallState<FallState.FallState>}.
    """
    def __init__(self, owner):
        State.__init__(self, owner, Constants.StateConstants.IDLE_NAME)
    
    def OnEnter(self):
        """
        Make sure the player is stopped and on the ground.
        """
        self._owner._color = pygame.Color(0, 255, 0)
        self._owner.Velocity = Vector((0, 0))
        self._owner.OnGround = True
        
    def Update(self, dt):
        """
        Process input, moves the Player (only gravity in this case), and checks for collisions.
                
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        # get some control stuff
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.InAir:
            self._owner.ChangeState('fall')
            
        self._owner.CurrentState.ProcessInput()
    # no exit state
    
    def ProcessInput(self):
        """
        Processes L{Player.Controller}, and possibly switches to L{RunState<RunState.RunState>} or L{JumpState<RunState.RunState>}.
        """
        controller = self._owner.Controller
        
        if (controller.dpad.Right.Down):
            self._owner.ChangeState('run')
        elif (controller.dpad.Left.Down):
            self._owner.ChangeState('run')
    
        elif (controller.Button(Constants.ControllerConstants.JUMP_BUTTON).Pressed):
            self._owner.ChangeState('jump')
            
        elif(controller.Button('Throw').Pressed):
            self._owner.ChangeState('throw')
            
######### JUMP #########            
            
class JumpState(PlayerState):
    """
    L{Player<Player.Player>} state for jumping.  Triggered by pressing the jump button.
    From here, Players can enter the L{FallState<FallState.FallState>}.
    """
    def __init__(self, owner):
        State.__init__(self, owner, Constants.StateConstants.JUMP_NAME)
    
    def OnEnter(self):
        """
        Force the player into the air and apply jump force.
        """
        self._owner._color = pygame.Color(0, 0, 255)
        self._owner.Velocity = (self._owner.Velocity.x, -self._owner.JumpVelocity)
        self._owner.InAir = True
        self._owner.PlayAnimation('launch')
        self._owner.QueueAnimation('jump')
        self._owner.PlaySound('jump')
        
        # cad test transfer
        self._owner._numjumps += 1
        #print self._owner, ' jumped ', self._owner._numjumps, 'times'
        
    def Update(self, dt):
        """
        Process input, move the Player, check for collisions, and possibly enter L{FallState<FallState.FallState>}.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        # going down, change into a fall
        if (self._owner.Velocity.y > 0.0):
            self._owner.ChangeState('fall')
        
        self._owner.CurrentState.ProcessInput()
            
    def ProcessInput(self):
        """
        Processes the L{Player.Controller} input and set velocities appropriately.
        """
        controller = self._owner.Controller
        
        if (controller.dpad.Right.Down):
            self._owner.Velocity = Vector((self._owner.RunVelocity, self._owner.Velocity.y))
        elif (controller.dpad.Left.Down):
            self._owner.Velocity = Vector((-self._owner.RunVelocity, self._owner.Velocity.y))
        else:
            self._owner.Velocity = Vector((0, self._owner.Velocity.y))
            
        if controller.Button('Throw').Pressed and not self._owner.AirThrow:
            self._owner.ChangeState('throw')
            
######### LAND ######### 

class LandState(PlayerState):
    """
    A transitional state between L{FallState<FallState.FallState>} and either L{RunState<RunState.RunState>}
    or L{IdleState<IdleState.IdleState>} for the L{Player<Player.Player>} class.
    """

    def __init__(self, owner):
        State.__init__(self, owner, Constants.StateConstants.LAND_NAME)
        
    def OnEnter(self):
        """
        Ensure the Player is on the ground and decide which state to switch to.
        """
        self._owner.OnGround = True
        self._owner.AirThrow = False
        self._owner.PlayAnimation('land')
        self._owner.PlaySound('land')
        self._owner.CurrentState.ProcessInput()
        
    def ProcessInput(self):
        """
        Decide which state to switch to: either L{RunState<RunState.RunState>} or L{IdleState<IdleState.IdleState>}
        """
        controller = self._owner.Controller
        
        if (controller.dpad.Right.Down):
            self._owner.ChangeState('run')
        elif (controller.dpad.Left.Down):
            self._owner.ChangeState('run')
        else:
            self._owner.ChangeState('idle')
            self._owner.QueueAnimation('idle')

######### RUN #########

class RunState(PlayerState):
    """
    L{Player<Player.Player>} state for running.  Triggered by Left/Right input on the controller while on the ground.
    From a here, a Player can enter the L{IdleState<IdleState.IdleState>}, L{JumpState<JumpState.JumpState>},
    or L{FallState<FallState.FallState>}.
    """
    def __init__(self, owner):
        State.__init__(self, owner, Constants.StateConstants.RUN_NAME)
        
    def OnEnter(self):
        """
        Ensure the Player is on the ground.
        """
        self._owner._color = pygame.Color(255, 0, 0)
        self._owner.OnGround = True
        self._owner.PlayAnimation('run')
       
        """
        # CAD - other run method
        # start running
        controller = self._owner.Controller
        if (controller.dpad.Right.Pressed):
            self.Run('right', False)
        elif (controller.dpad.Left.Pressed):
            self.Run('left', False)
        """
        #cad test
        #self._owner._sounds['count down'].Play()
        #self._owner.PlaySound('count down')
    def OnExit(self):
        #cad test
        
        return
        
    def Update(self, dt):
        """
        Process input, move the Player, and check for collisions.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        # sooooooo ghetto - cad
        if self._owner.InAir and self._owner._currentState.Name == self.Name:
            self._owner.ChangeState('fall')
        
        self._owner.CurrentState.ProcessInput()
        
    def ProcessInput(self):
        """
        Processes the L{Player.Controller} input and decide which state to be in.
        """
        controller = self._owner.Controller
        
        if (controller.Button(Constants.ControllerConstants.JUMP_BUTTON).Pressed):
            self._owner.ChangeState('jump')
        elif(controller.Button('Throw').Pressed):
            self._owner.ChangeState('throw')
        elif (controller.dpad.Right.Down):
            self._owner.Velocity = Vector((self._owner.RunVelocity, self._owner.Velocity.y))
            self._owner.FacingRight = True
        elif (controller.dpad.Left.Down):
            self._owner.Velocity = Vector((-self._owner.RunVelocity, self._owner.Velocity.y))
            self._owner.FacingLeft = True
        else:
            self._owner.ChangeState('idle')
            self._owner.PlayAnimation('idle')
        
        """
        # CAD - other run method
        # jump button
        if (controller.Button(Constants.ControllerConstants.JUMP_BUTTON).Pressed):
            self._owner.ChangeState('jump')
        # left and right are UP
        elif (controller.dpad.Left.Up and controller.dpad.Right.Up):
            self._owner.ChangeState('idle')
        # left and right are DOWN
        elif (controller.dpad.Left.Down and controller.dpad.Right.Down):
            if (self._owner.FacingRight and controller.dpad.Left.Pressed):
                self.Run('left', True)
            elif (self._owner.FacingLeft and controller.dpad.Right.Pressed):
                self.Run('right', True)
        # only left or right is down, but we need to switch direction
        else:
            if (controller.dpad.Right.Down and self._owner.FacingLeft):
                self.Run('right', True)
            elif (controller.dpad.Left.Down and self._owner.FacingRight):
                self.Run('left', True)
        """
    
    def Run(self, direction, switching):
        """
        Used for alternate run method.
        """
        runVel = self._owner.RunVelocity
        
        if (direction == 'left'):
            runVel *= -1
            self._owner.FacingLeft = True
        else:
            self._owner.FacingRight = True
            
        if (switching):
            runVel *= 2
          
        self._owner.Velocity += Vector((runVel, 0))
        
######### THROW #########

class ThrowState(PlayerState):
    """
    L{Player<Player.Player>} state for jumping.  Triggered by pressing the jump button.
    From here, Players can enter the L{FallState<FallState.FallState>}.
    """
    def __init__(self, owner):
        State.__init__(self, owner, Constants.StateConstants.THROW_NAME)
        
        self._activateFrame = 1
        self._deactivateFrame = 3
        
        
    def OnEnter(self):
        self._owner._color = pygame.Color(255, 174, 0)
        self._owner._throwCoolDown = Constants.PlayerConstants.THROW_COOLDOWN
        
        if self._owner.Controller.dpad.Left.Down:
            self._owner.FacingLeft = True
        elif self._owner.Controller.dpad.Right.Down:
            self._owner.FacingRight = True
        
        d = self._owner.Controller.dpad.Direction
        d = d.safe_normalised()
        d = Vector((d.x * self._owner.ThrowVel.x, d.y * self._owner.ThrowVel.y))
        
        if d.is_zero:
            d = Constants.PlayerConstants.DEFAULT_THROW_VECTOR
            if self._owner.FacingLeft:
                d = Vector((-1 * d.x, d.y))
                
        elif d.y == 0:
            d = Vector((d.x, Constants.PlayerConstants.DEFAULT_THROW_VECTOR.y))
        
        if self._owner.OnGround and d.y > Constants.PlayerConstants.DEFAULT_THROW_VECTOR.y:
            d = Vector((d.x, Constants.PlayerConstants.DEFAULT_THROW_VECTOR.y))
        
        self._owner.ThrowVector = d
        
        self._owner.PlayAnimation('throw')
        # cad sound test
        self._owner.PlaySound('swipe')
        
        self._totalFrames = self._owner.ThrowFrames
        if self._owner.InAir:
            self._owner.AirThrow = True
        
    def Update(self, dt):
        self._totalFrames -= 1
        
        
        if self._owner.CurrentAnimation.FrameNum == self._activateFrame:
            self._owner.isThrowing = True
            
        if self._owner.CurrentAnimation.FrameNum == self._deactivateFrame:
            self._owner.isThrowing = False
        
        if self._totalFrames < 0:
            if not self._owner.AirThrow:
                self._owner.ChangeState('idle')
                self._owner.PlayAnimation('idle')
            else:
                self._owner.ChangeState('fall')
                
                
    def OnExit(self):
        # make sure we're not throwing anymore
        self._owner.isThrowing = False
        self._owner.Velocity = Vector((0, 0))
        

######### THROWN #########
class ThrownState(PlayerState):
    """
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'thrown')
        
    def OnEnter(self):
        self._owner._color = pygame.Color(255, 107, 216)
        
        self._owner.Velocity = Vector((0, 0))
        
        self._owner.InAir = True
        # make invulnerable
        self._owner.isThrown = True
        
        self._owner.PlayAnimation('thrown')
        self._owner.PlaySound('hit')
        
    def Update(self, dt):
        """
        Process input, move the Player, and check for collisions.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.OnGround:
            self._owner.ChangeState('land')
            
    def OnExit(self):
        # play getup, queue idle animation?
        #self._owner.PlayAnimation('idle')
        # make vulnerable
        self._owner.isThrown = False
        return
    
    
######### DEAD #########
class DeadState(PlayerState):
    """
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'dead')
        
        self._respawnCountDown = 0.0
        
    def OnEnter(self):
        self._owner._color = pygame.Color(0, 107, 216)
        
        self._respawnCountDown = self._owner.respawnTime
        #self._owner.Velocity = Vector((0, 0))
        
        self._owner.PlayAnimation('dead')
        self._owner.PlaySound('hit')
        
        #self._owner.ApplyEffect(BlinkEffect(self._owner, self._respawnCountDown, 0.25))
        
        # make invulnerable
        self._owner.isThrown = True
        
    def Update(self, dt):
        """
        Process input, move the Player, and check for collisions.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        """
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.OnGround:
            self._owner.ChangeState('land')
        """
        
        #self._owner.Velocity = Vector((0, 0))
        #self._owner.__update_position__(dt)
        #self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        self._respawnCountDown -= dt
        if self._respawnCountDown <= 0.0:
            self._owner.ChangeState('fall')
            
    def OnExit(self):
        # play getup, queue idle animation?
        #self._owner.PlayAnimation('idle')
        
        self._owner.Velocity = Vector((0, 0))
        
        self._owner.FacingRight = self._owner.RespawnFacingRight
        self._owner.Position = self._owner.RespawnPosition
        
        # make vulnerable
        self._owner.isThrown = False
        self._owner.ApplyEffect(BlinkEffect(self._owner, self._owner.respawnTime, 0.25))
    
    
######### WIN #########
class WinState(PlayerState):
    """
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'win')
        self._winTimer = 0.0
        
        self._isOnGround = False
        self._wasInAir = False

        
    def OnEnter(self):
        
        if self._owner.Lose:
            self._owner.ChangeState('lose')
            return
        
        self._owner.Velocity = Vector((0, self._owner.Velocity.y))
        
        self._owner._color = pygame.Color(255, 255, 255)
        self._owner.PlayAnimation('win')
        self._owner.PlaySound('win')
        
        self._winTimer = 2.8
        
        self._isOnGround = self._owner.OnGround
        self._wasInAir = self._owner.InAir
        
        
    def Update(self, dt):
        """
        Process input, move the Player, and check for collisions.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        """
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.OnGround:
            self._owner.ChangeState('land')
        """

        #self._owner.Velocity = Vector((0, 0))
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        self._isOnGround = self._owner.OnGround
        
        #process
        if self._wasInAir and self._isOnGround:
            self._owner.PlaySound('land')
        
        
        self._wasInAir = self._owner.InAir
        
        self._winTimer -= dt
        if self._winTimer < 0.0:
            self._owner.Win = True
         
    def OnExit(self):
        # play getup, queue idle animation?
        self._owner.PlayAnimation('idle')

######### LOSE #########
class LoseState(PlayerState):
    """
    """
    def __init__(self, owner):
        State.__init__(self, owner, 'lose')
        
        self._isOnGround = False
        self._wasInAir = False
        
    def OnEnter(self):
        self._owner._color = pygame.Color(20, 20, 20)
        self._owner.PlayAnimation('dead')

        self._owner.Lose = True
        
        self._owner.Velocity = Vector((0, 0))
        
        
        
        self._isOnGround = self._owner.OnGround
        self._wasInAir = self._owner.InAir
        
    def Update(self, dt):
        """
        Process input, move the Player, and check for collisions.
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        """
        
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        if self._owner.OnGround:
            self._owner.ChangeState('land')
        """

        #self._owner.Velocity = Vector((0, 0))
        self._owner.__update_position__(dt)
        self._owner.__check_resolve_env_collisions__(self._owner.Map.Layer(Constants.EditorConstants.LAYER_NAME_COLLISION_TILES))
        
        
        self._isOnGround = self._owner.OnGround
        
        #process
        if self._wasInAir and self._isOnGround:
            self._owner.PlaySound('land')
        
        
        self._wasInAir = self._owner.InAir
         
    def OnExit(self):
        # play getup, queue idle animation?
        self._owner.PlayAnimation('idle')

    
################## BLINK EFFECT ##################         
        
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
        
        # add ability to not get thrown
        self._owner.isThrown = True
        
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
        
        # ability to get thrown again
        self._owner.isThrown = False