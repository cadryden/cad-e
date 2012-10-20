'''
B{[Base Class]} The base class for all entities that exist in the game world.

@author: Chris Alvarado-Dryden
'''

import pygame
from Core import Constants
from Utilities.vector import Vector

from collections import deque

class GameObject(object):
    """
    B{[Base Class]} The GameObject is the base class for all entities that exist in the game world. Each has a bounding
    box for collisions, a position in world coordinates, and an image to be drawn to the screen.  A vanilla GameObject
    is static and does not update regularly as the game runs.  They can, however, react and animate.  For more dynamic
    entities, which update every frame, see the L{Actor<Actor.Actor>} class.
    
    
    @type boundingBox:            U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar boundingBox:            An axis aligned rectangle that is used for processing, including
                                  collision, movement, and positions.
        
    @type image:                  U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar image:                  Image that should be drawn at the object's L{Position}
        
    @type _debugImage:            U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _debugImage:            Image which will be drawn if using debug draw.  It is a 
                                  visual representation of the bounding box.
                                      
    @type Visible:                C{bool}
    @ivar Visible:                C{True} if should be drawn, C{False} otherwise.
    
    @type _drawPoint:             C{(int, int)}
    @ivar _drawPoint:             Where in the world to draw the top left corner of this object's image.  If C{None},
                                  L{Position} will be used.
    
    @type _name:                  C{str}
    @ivar _name:                  Name of the object from the U{Tiled editor<http://www.mapeditor.org/>}.
    
    @type _animations:            C{dict}
    @ivar _animations:            C{{str : L{Animation<Animation.Animation>}}} - Dictionary of this GameObject's animations
                                  and their names.
    
    @type _drawOffsets:           C{dict}
    @ivar _drawOffsets:           C{{L{Animation<Animation.Animation>} : L{Vector<Utitlities.vector.Vector>}}} - Dictionary
                                  of animations and the relative positions their frames should be drawn at.  Offsets are
                                  relative to the GameObject's L{Position}.  These are used as draw points.
    
    @type _animationQueue:        C{U{collections.deque<http://docs.python.org/library/collections.html#deque-objects>}}
    @ivar _animationQueue:        Queue of L{Animation<Animation.Animation>}s that this GameObject should play.  When the top
                                  animation is complete, it is stopped and popped off the queue.  If there's only 1
                                  animation in the queue, it will not be popped.
                                  
    @type _sounds:                C{dict}
    @ivar _sounds:                C{{str : L{Sound<Sound.Sound>}}} - Dictionary of this GameObject's sounds and their names.
    
    @type _playingSounds:         C{list}
    @ivar _playingSounds:         List of all L{Sound<Sound.Sound>}s that this GameObject is currently playing.
    """

    @staticmethod
    def PropertiesToParameters(properties):
        """
        Takes the values of the passed in dictionary and arranges them into an appropriate parameter list for object construction.
        In addition to the U{Tiled<http://mapeditor.org/>} Properties, the dictionary will also include position,
        width, and height.
        
        @type  properties:    C{dict}
        @param properties:    C{{unicode : unicode}} - A dictionary of property names and their values.
        
        @rtype:               C{list}
        @return:              Values of the properties to be used as parameters, in parameter list order for the constructor.
        """
        params = []
        
        params.append((properties['x'], properties['y']))
        params.append(properties['width'])
        params.append(properties['height'])
        params.append(properties['name'])
        
        return params

    def __init__(self, position, width, height, layer, name='', image=None, animationMappings=None, soundMappings=None):
        """
        Creates a new GameObject at the given position, with the given dimensions.
        
        @type  position:             C{(int, int)} | L{Vector<Utilities.vector.Vector>}
        @param position:             World coordinates of the top left corner of the object's bounding box
        
        @type  width:                C{int}
        @param width:                Width of the object's bounding box in pixels.
        
        @type  height:               C{int}
        @param height:               Height of the object's bounding box in pixels.
        
        @type  layer:                L{GameLayer<Map.GameLayer.GameLayer>}
        @param layer:                The GameLayer this object is on.
        
        @type  name:                 C{str}
        @param name:                 Name of the object from the U{Tiled editor<http://www.mapeditor.org/>}.
        
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
        """
        self.boundingBox = pygame.Rect(position, (width, height))
        self._layer = layer
        self.image = image
        self._debugImage = None
        self.Visible = True
        self._drawPoint = None
        
        # animations
        self._animations = {}
        self._drawOffsets = {}
        self._animationQueue = deque()
        
        if animationMappings:
            for animPack in animationMappings:
                animName = animPack[0]
                anim = animPack[1]
                offset = animPack[2]
                self._animations[animName] = anim
                self._drawOffsets[anim] = offset
        
        # sounds
        self._sounds = {}
        self._playingSounds = []

        if soundMappings:
            for soundPack in soundMappings:
                soundName = soundPack[0]
                sound = soundPack[1]
                self._sounds[soundName] = sound
        
        if (name):
            self._name = name
        else:
            self._name = object.__str__(self)
        
    def Collides(self, other):
        """
        A generic collision detection method.  Returns C{True} if the two bounding boxes overlap.
        
        @type  other:    C{GameObject}
        @param other:    The other GameObject to test collision against.
        
        @rtype:          C{bool}
        @return:         C{True} if the two bounding boxes overlap, C{False} otherwise.
        """
        return self.boundingBox.colliderect(other.boundingBox)
    
    def ResolveCollision(self, other):
        """
        B{[Stub]} Resolves the collision between this GameObject and the given one.  This is a stub method and should be overridden
        by child classes.
        
        @type  other:    GameObject
        @param other:    GameObject this object is colliding with.
        """         
        return
    
    def PlayAnimation(self, animationName, startFrame=0):
        """
        Plays the GameObject's L{Animation<Animation.Animation>} with the given name.  All other animations in
        the queue will be stopped and removed.
        
        @type  animationName:    C{str}
        @param animationName:    Name of the animation to play.
        
        @type  startFrame:       C{int}
        @param startFrame:       Which numbered frame to begin playing on.  Defaults to start from the beginning.
        """
        # stop animations and clear it out
        for anim in self._animationQueue:
            anim.Stop()
        self._animationQueue.clear()
        # play the given animation
        self._animationQueue.append(self._animations[animationName])
        self._animationQueue[0].Play(startFrame)
    
    def QueueAnimation(self, animationName):  
        """
        Queues the GameObject's L{Animation<Animation.Animation>} with the given name.  The animation will play
        when all animations queued ahead of it have completed.
            
        @type  animationName:    C{str}
        @param animationName:    Name of the animation to queue.
        """  
        self._animationQueue.append(self._animations[animationName])
        
    def PlaySound(self, soundName):
        """
        Plays the GameObject's L{Sound<Sound.Sound>} with the given name.  If the GameObject is already playing
        the sound, it will be restarted.
        
        @type  soundName:        C{str}
        @param soundName:        Name of the sound to play.
        """        
        self.__cleanup_soundlist__()

        sound = self._sounds[soundName]
        if sound in self._playingSounds:
            sound.Stop()
        else:
            self._playingSounds.append(sound)
        sound.Play()
        
    def PlaySoundConcurrent(self, soundName):
        """
        Plays the GameObject's L{Sound<Sound.Sound>} with the given name on top of I{all} of its other sounds.
        If the Sound is already playing, a copy is made and then played from the beginning. 
        
        @type  soundName:        C{str}
        @param soundName:        Name of the sound to play.
        
        @rtype:                  L{Sound<Sound.Sound>}
        @return:                 Sound that will be played.
        """
        self.__cleanup_soundlist__()

        sound = self._sounds[soundName].Copy()
        self._playingSounds.append(sound)
        sound.Play()
        return sound
        
    def __cleanup_soundlist__(self):
        """
        Cleans out old L{Sound<Sound.Sound>}s from the list of currently playing sounds.
        """
        for sound in list(self._playingSounds):
            if not (sound.Playing or sound.Paused):
                sound.Stop()
                self._playingSounds.remove(sound)

    def StopSounds(self):
        """
        Stops all L{Sound<Sound.Sound>}s this GameObject is playing.
        """
        for sound in self._playingSounds:
            sound.Stop()
            
    def PauseSounds(self):
        """
        Pauses all L{Sound<Sound.Sound>}s this GameObject is playing.
        """
        for sound in self._playingSounds:
            sound.Pause()
            
    def ResumeSounds(self):
        """
        Resumes all L{Sound<Sound.Sound>}s this GameObject was playing.
        """
        for sound in self._playingSounds:
            sound.Play()

    def Draw(self, cameras, transformations=[], debug=False):
        """
        Sends the GameObject's image to each L{Camera<Utilities.Camera.Camera>}to be drawn if it is within
        the camera's field of view.  If there are passed in transformation functions, those are executed with
        the image and their passed in parameters before being sent to the cameras. 
        
        If the C{debug} flag is set to C{True}, it will instead draw the GameObject's
        bounding box.
        
        @type  cameras:            C{list}
        @param cameras:            The list of L{Camera<Utilities.Camera.Camera>}s objects that should try to be drawn to.
        
        @type  transformations:    C{list}
        @param transformations:    List of tuples that are C{(function, list)} pairs.  The functions
                                   are from C{U{pygame.transform<http://www.pygame.org/docs/ref/transform.html>}}, and
                                   their parameter lists should not include the 
                                   C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}} that each C{pygame.transform}
                                   function expects.  It is assumed assumed the transform will be applied to this object's
                                   image.
                                   
        @type  debug:              C{bool}
        @param debug:              If C{True}, the bounding box will be drawn instead of the GameObject's image.
        """
        
        # don't bother if we can't be seen
        if (not self.Visible):
            return
        
        image = self.image
        
        # default draw to the top left of bounding box
        drawPoint = self.Position
        if (self._drawPoint):
            drawPoint = self._drawPoint
        
        if debug:
            # debug mode is the bounding box
            drawPoint = self.Position
            # load an image for bounding box once
            if self._debugImage == None:
                self._debugImage = pygame.Surface((self.Width, self.Height))
                self._debugImage = self._debugImage.convert_alpha()
                self._debugImage.fill(Constants.GameObjectConstants.DEBUG_COLOR)
                
                image = self._debugImage
        else:
            # going to play some animations
            if(len(self._animationQueue) > 0):
                # which one to play?
                if self._animationQueue[0].Completed and len(self._animationQueue) > 1:
                    oldAnim = self._animationQueue.popleft()
                    oldAnim.Stop()
                    self._animationQueue[0].Play()
                
                image = self._animationQueue[0].GetFrame()
                # draw it a the right place
                drawPoint = self.Position + self._drawOffsets[self._animationQueue[0]]
            else:
                image = self.image
            
        # apply transformations
        for transform in transformations:
            func = transform[0]
            params = [image]
            for param in transform[1]:
                params.append(param)
            image = func(*params)
            
        for camera in cameras:
            if (debug):    
                camera.Draw(image, drawPoint)
            else:
                camera.Draw(image, drawPoint)    

    def __str__(self):
        """
        Name of the GameObject.  If no name was set, it will return C{object.__str__()}.
        
        @rtype:     C{str}
        @return:    String representation the GameObject.
        """
        return self.Name
    
    ############### PROPERTIES ###############
    
    def __get_position__(self):
        """
        @rtype:    C{(int, int)}
        """
        return self.boundingBox.topleft
    def __set_position__(self, pos):
        """
        @type pos:    C{(int, int)} | L{Vector<Utilities.vector.Vector>}
        """
        self.boundingBox.topleft = (round(pos[0], 0), round(pos[1], 0))
    def __get_center__(self):
        """
        @rtype:    C{(int, int)}
        """
        return self.boundingBox.center
    def __set_center__(self, pos):
        """
        @type pos: C{(int, int)} | L{Vector<Utilities.vector.Vector>}
        """
        if (isinstance(pos, Vector)):
            pos = (pos.x, pos.y)
        self.boundingBox.center = pos
    def __get_width__(self):
        """
        @rtype:    C{int}
        """
        return self.boundingBox.width
    def __get_height__(self):
        """
        @rtype:    C{int}
        """
        return self.boundingBox.height
    def __get_name__(self):
        """
        @rtype:    C{str}
        """
        return self._name
    
    def __get_animation__(self):
        """
        @rtype:     L{Animation<Core.Animation.Animation>}
        """
        if len(self._animationQueue) == 0:
            return None
        else:
            return self._animationQueue[0]
        
    def __get_layer__(self):
        return self._layer
    
    Position = property(__get_position__, __set_position__, None, "Bounding box's upper left corner in world coordinates.")
    Center = property(__get_center__, __set_center__, None, "Bounding box's center in world coordinates.")
    Width = property(__get_width__, None, None, "Bounding box's width in pixels.")
    Height = property(__get_height__, None, None, "Bounding box's height in pixels.")
    Name = property(__get_name__, None, None, "The name of this object.")
    CurrentAnimation = property(__get_animation__, None, None, "The current animation, None if no animation is playing.")
    Layer = property(__get_layer__, None, None, "The L{GameLayer<Map.GameLayer.GameLayer>} this tile is on.") 