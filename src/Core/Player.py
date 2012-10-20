'''
An L{Actor<Actor.Actor>} with a L{Controller<Utilities.Controller.Controller.Controller>}.

@author: Chris Alvarado-Dryden
'''

from Core import Constants
from Core.Actor import Actor

class Player(Actor):
    """
    A Player is an L{Actor<Actor.Actor>} with a L{Controller<Utilities.Controller.Controller.Controller>}.
    Here, input processing is done via L{State<State.State>}s.

    @type _controller:    L{Controller<Utilities.Controller.Controller>}
    @ivar _controller:    Input device for this Player.

    @type PlayerNum:      C{int}
    @ivar PlayerNum:      The Player's number, as in Player 1, Player 2, etc.
    """
    
    @staticmethod
    def PropertiesToParameters(properties):
        """
        Translates the I{player} property into the player number in addition to its parents' properties.
        """
        params = Actor.PropertiesToParameters(properties)
        
        # check player number
        if (Constants.EditorConstants.OBJ_PLAYER_PROP_PLAYER_NUMBER in properties and properties[Constants.EditorConstants.OBJ_PLAYER_PROP_PLAYER_NUMBER].strip()):
            # assume Player 1 is really 0
            playerNum = int(properties[Constants.EditorConstants.OBJ_PLAYER_PROP_PLAYER_NUMBER]) - 1
        else:
            playerNum = 0
        
        params.append(playerNum)        
        #controller gets none
        params.append(None)
        
        return params
    
    def __init__(self, position, width, height, name, collisionGroupNames, transferName, playerNum, controller, stateMappings={}, startStateName='', image=None, animationMappings=None, soundMappings=None):
        """
        Creates a new Player at the given position, with a bounding box having the given width and height,
        and associated controller for input gathering.
        
        @type  position:             C{(int, int) | L{Vector<Utilities.vector.Vector>}}
        @param position:             World coordinates of the top left corner of the object's bounding box
        
        @type  width:                C{int}
        @param width:                Width of the object's bounding box in pixels.
        
        @type  height:               C{int}
        @param height:               Height of the object's bounding box in pixels.
        
        @type  collisionGroupNames:  C{list}
        @param collisionGroupNames:  List of names (C{str}) of L{CollisionGroup<CollisionGroup.CollisionGroup>}s that
                                     this Actor should be part of.
        
        @type  transferName:         C{str}
        @param transferName:         Name of the Actor to transfer attributes from when switching between maps.  
        
        @type  playerNum:            C{int}
        @param playerNum:            Player number from the U{Tiled's<http://mapeditor.org/>} .TMX map file.  In the editor
                                     this is 1-based, but internally it is 0-based.
        
        @type  controller:           L{Controller<Utilities.Controller.Controller.Controller>}
        @param controller:           Where the Player will be getting its input.  When loading a Player from a map, this will
                                     be C{None}.  The Controller will be associated to the player during map load instead of
                                     when the constructor is called.
        
        @type  stateMappings:        C{list}
        @param stateMappings:        List of pairs in the form C{str, L{State<State.State>}} which are the States available to
                                     this Actor.  In detail they are:
                                         - C{str} - Name to use to refer to this State.
                                         - C{State} - The State object.
        
        @type  startStateName:       C{str}
        @param startStateName:       Name of the L{State<State.State>} the Actor will start in.
        
        @type  image:                U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
        @param image:                The static image that should be drawn at the object's L{Position}.
        
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
        """
        # pass up the states
        Actor.__init__(self, position, width, height, name, collisionGroupNames, transferName, stateMappings, startStateName, image, animationMappings, soundMappings)
        
        # we have a controller
        self._controller = controller
        
        # for loading from editor
        self.PlayerNum = playerNum
                            
    ############### PROPERTIES ###############
    
    def __get_controller__(self):
        return self._controller
    def __set_controller__(self, value):
        self._controller = value
        
    Controller = property(__get_controller__, __set_controller__, None, "L{Controller<Utilities.Controller.Controller.Controller>} bound to this Player.")