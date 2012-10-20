'''
B{[Base Class]} A single state in a finite state machine.

@author: Chris Alvarado-Dryden
'''

class State(object):
    """
    B{[Base Class]} A single state in a finite state machine.  Each State has functions that are called when
    the state is entered, when it is exited, and on each update.  States are used as a basis for gameplay programming.
    
    @type _owner:    L{Actor<Actor.Actor>}
    @ivar _owner:    Who this State belongs to.
    
    @type _name:     C{str}
    @ivar _name:     The name of this State.
    """
    
    def __init__(self, owner, name):
        """
        Create the State with the given owner and name.
        
        @type  owner:    L{Actor<Actor.Actor>}
        @param owner:    Who this State belongs to.
        
        @type  name:     C{str}
        @param name:     The name of this State.
        """
        self._owner = owner
        self._name = name
        
    def OnEnter(self):
        """
        B{[Stub]} Called whenever the owner changes to this State, should be overridden in child classes.
        """
        return
    
    def Update(self, dt):
        """
        B{[Stub]} Called every frame as part of the owner's L{update<Core.Actor.Actor.Update>}.  This is where most of the logic
        happens.  Should be overridden in child classes
        
        @type  dt:    C{float}
        @param dt:    The time in seconds since the last frame refresh.
        """
        return
    
    def OnExit(self):
        """
        B{[Stub]} Called whenever the owner changes to a different State should be overridden in child classes.
        """
        return
    
    def __str__(self):
        """
        State's name and its owner.
        
        @rtype:     C{str}
        @return:    String representation of this State.
        """
        return self.Name + ' owned by ' + self._owner.__str__()
    
    def __get_name__(self):
        return self._name
    Name = property(__get_name__, None, None, "Name of this State.")