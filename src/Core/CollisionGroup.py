'''
A structure to organize the collision checks between L{Actor<Actor.Actor>}s.

@author: Chris Alvarado-Dryden
'''

from Core import Constants

class CollisionGroup(object):
    """  
    A structure to organize the collision checks between L{Actor<Actor.Actor>}s.  A CollisionGroup is a collection
    of objects (members), and a list of other CollisionGroups.  Each member of a group will perform the same checks as every
    other member in that group.  Those checks will be against all members of the groups this CollisionGroup has listed.
    
    For example::
    
        Group:            Player    |   NPC
                          ----------|---------
        Members:          player1   |   npc1
                          player2   |   npc2
                                    |
        Collides With:    Player    |   Player
                          NPC       |   
    
    I{player1} and I{player2} can collide with each other and the two NPCs, but I{npc1} and I{npc2} cannot collide with each other.
     
    @type _members:             C{list}
    @ivar _members:             All L{Actor<Actor.Actor>}s that are part of this group.
    
    @type _collidableGroups:    C{list}
    @ivar _collidableGroups:    All CollisionGroups that this group collides with.
    
    @type collidesWithNames:    C{list}
    @ivar collidesWithNames:    Names (C{str}) of CollisionGroups from the map editor, used to coordinate group interactions. 
    """

    @staticmethod
    def PropertiesToParameters(properties):
        """
        Translates the I{collides with} property from the map file into parameters.
        
        @type  properties:    C{dict}
        @param properties:    C{{unicode : unicode}} - A dictionary of property names to values.
        
        @rtype:               C{list}
        @return:              Values of the properties to be used as parameters, in parameter list order for the constructor.
        """
        params = []
        
        nameList = []
        if properties.has_key(Constants.EditorConstants.OBJ_CG_PROP_COLLIDES_WITH) and properties[Constants.EditorConstants.OBJ_CG_PROP_COLLIDES_WITH].strip():
            nameList = properties[Constants.EditorConstants.OBJ_CG_PROP_COLLIDES_WITH]
            nameList = map(unicode.strip, nameList.split(','))
        
        params.append(properties['name'])
        params.append(None)
        params.append(None)
        params.append(nameList)
        
        return params
    
    def __init__(self, name, members=None, collidesWith=None, collidesWithNames=None):
        """
        Creates a new CollisionGroup with the given name, and members, and will collide with the given groups.
        If using the C{collidesWithNames} parameter, then C{collidesWith} should be C{None}, and vice versa.
        Currently, C{collidesWithNames} is only used to coordinate CollisionGroups when a map is loaded.
        
        @type  name:                C{str}
        @param name:                Name of this CollisionGroup.
        
        @type  members:             C{list}
        @param members:             List of L{Actor<Actor.Actor>}s, this group can collide with.
        
        @type  collidesWith:        C{list}
        @param collidesWith:        List of CollisionGroups that members of this group can collide with.
        
        @type  collidesWithNames:   C{list}
        @param collidesWithNames:   List of names (C{str}) that indicate each of the collision groups this group should collide with.
                                    This is a bit of kludge to load the groups directly from the map editor. 
        """
        self._name = name
        
        self._members = []
        if (members):
            self._members.extend(members)
            
        # add collidables to this group if any exist
        self._collidableGroups = []
        if (collidesWith):
            self._collidableGroups.extend(collidesWith)

        self.collidesWithNames = []
        if (collidesWithNames):
            self.collidesWithNames.extend(collidesWithNames)
        
        
    def __assign_collision_groups__(self, nameToCGroup):
        """
        Assigns collisions in this group based on the given dictionary.  This is used when loading the level,
        to coordinate all of the CollisionGroups.
        
        @type  nameToCGroup:    C{dict}
        @param nameToCGroup:    C{{str : CollisionGroup}} - Name to CollisionGroup dictionary of all CollisionGroups in a map. 
        """
        for name in self.collidesWithNames:
            if name not in nameToCGroup:
                raise Exception('Check map file: Collision Group "' + name + '" not defined')
            else:
                self._collidableGroups.append(nameToCGroup[name])
                
    def AddMember(self, toAdd):
        """
        Add the given Actor to this CollisionGroup.
        
        @type  toAdd:    L{Actor<Actor.Actor>}
        @param toAdd:    Actor to add to this CollisionGroup.
        """
        self._members.append(toAdd)
        if not self in toAdd.CollisionGroups:
            toAdd.CollisionGroups.append(self)
            
    def AddCollisionGroup(self, toAdd):
        """
        Add the given CollisionGroup to the list of groups to collide with.
        
        @type  toAdd:    C{CollisionGroup}
        @param toAdd:    Additional group to check collisions against.
        """
        if toAdd not in self._collidableGroups:
            self._collidableGroups.append(toAdd)
        
    def CollidableSet(self):
        """
        Gets a set of all objects that this CollisionGroup should collide with. 
        
        @rtype:     C{set}
        @return:    Set of all objects that collide with this group.
        """
        collidables = set()
        for group in self._collidableGroups:
            collidables = collidables.union(set(group.Members))
        
        return collidables

    ############### PROPERTIES ###############
    def __get_name__(self):
        return self._name
    def __get_members__(self):
        return self._members
    
    Name = property(__get_name__, None, None, "Name of this CollisionGroup.")
    Members = property(__get_members__, None, None, "All members of this CollisionGroup.")