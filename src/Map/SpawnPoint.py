"""
Used to spawn objects that were placed via the U{Tiled<http://mapeditor.org/>} map editor.

@author: Chris Alvarado-Dryden
"""

import Utilities.HelperFunctions

class SpawnPoint(object):
    """
    A point in world space where an object will be created.  SpawnPoints are used to translate  map objects from
    U{Tiled<http://mapeditor.org/>} into game objects in the world.  When placing an object in Tiled, the SpawnPoint
    reads the following data:
        - type
        - (x, y) location
        - width
        - height
        - properties
        
    In order to use a SpawnPoint, ensure that the spawning object has or inherits a
    L{PropertiesToParameters<Core.Actor.Actor.PropertiesToParameters>} function in order to properly process any properties
    from the editor.
    
    @note:  When adding type information, the engine assumes that the class name and module name are the same (MyActor.MyActor for example).
            For more information on using U{Tiled<http://mapeditor.org/>} with CAD-E, consult this U{mapping tutorial<http://eventually-i-promise.com>}
            (eventually).
    
    @type _spawnClass:    C{class}
    @ivar _spawnClass:    The class to spawn. 
    
    @type _point:         C{(int, int)}
    @ivar _point:         The world coordinates to spawn at. 
    
    @type _spawnParams:   C{list}
    @ivar _spawnParams:   Additional parameters to pass when spawning.
    """
    
    #def __init__(self, typeName, worldCoords, props):
    def __init__(self, typeName, props):
        """
        Creates a SpawnPonit of the given type, with the given properties.  To correctly process
        the properties, the class being spawned should have a C{PropertiesToParameters} function similar to
        L{Actor.PropertiesToParameters<Core.Actor.Actor.PropertiesToParameters>}.
        
        @type  typeName:        C{str}
        @param typeName:        The name of the class/module to be spawned.  Assumes all classes are in their own .PY file and have
                                the same name as the module.
                                For example:
                                    - If module C{MyActor} is outside of other packages, C{typeName} will be C{'MyActor'}
                                    - If the C{MyActor} module is within the C{Actors} package, then C{typeName} will be C{'Actors.MyActor'}  
        
        @type  props:           C{dict}
        @param props:           C{{unicode : unicode}} - A dictionary of property names and their values taken from the Tiled .TMX file.
        """
        #self._point = worldCoords
        self._spawnParams = props
        
        self._spawnClass = Utilities.HelperFunctions.ReflectionFunctions.GetPythonClass(typeName)
        self._spawnParams = self._spawnClass.PropertiesToParameters(props)
        
        # pretty useless atm.  do i actually need to have it? - CAD
        self._point = self._spawnParams[0]
        
        
        #Old comment, keep if I decide to put it back - CAD
        #Creates a SpawnPonit of the given type, at the given position, and with any additional properties.  To correctly process
        #the properties, the class being spawned should have a C{PropertiesToParameters} function similar to
        #L{Actors<Actor.Actor.PropertiesToParameters>}.
        #
        #@type  worldCoords:     C{(int, int)}
        #@param worldCoords:     The position at which to spawn the object.  This will be the object's position.
        
        
    def Spawn(self):
        """
        Constructs an object of the associated type.
        
        @rtype:        C{instance}
        @return:       An instance of the class this SpawnPoint creates. 
        """
        entity = self._spawnClass(*self._spawnParams)
        
        return entity
    
    ############### PROPERTIES ###############
        
    def __get_className__(self):
        return self._spawnClass.__name__
    ClassName = property(__get_className__, None, None, "The name of the class this spawns.")