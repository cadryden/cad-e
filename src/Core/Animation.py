'''
A series of frames in a sprite sheet, used to create animated sprites.

@author: Chris Alvarado-Dyden
'''

import pygame.image

class Animation(object):
    """
    A series of frames in a sprite sheet, used to create animated sprites.  Frames should be organized left to right, and each
    should be the same dimensions.
    
    Sheets can be images with alpha values (like .TGA or .PNG), or they can be color-keyed without alpha values.
    
    @type loadedSpriteSheets:        C{dict}
    @cvar loadedSpriteSheets:        C{{str : Animation}} - A dictionary of sprite sheet paths and their
                                     C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}} objects.  This is used to prevent
                                     reloading the same sprite sheet multiple times.  It is populated as animations are loaded.
                                     
    @type _spriteSheet:              C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
    @ivar _spriteSheet:              The sprite sheet image that holds all of the frames for this animation.
    
    @type _startPos:                 C{(int, int)}
    @ivar _startPos:                 Coordinates for the top left of the first frame of this animation within the sprite sheet. 
    
    @type _frame:                    C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
    @ivar _frame:                    Subsurface within the sprite sheet for the current frame of animation.
    
    @type _frameNum:                 C{int}
    @ivar _frameNum:                 Which numbered frame the animation is currently on.
    
    @type _totalFrames:              C{int}
    @ivar _totalFrames:              Total number of frames in this animation.
    
    @type _frameDelay:               C{int}
    @ivar _frameDelay:               How many frames of the game should pass (render frames) before switching to the next animation frame.
    
    @type _framesUntilChange:        C{int}
    @ivar _framesUntilChange:        How many more render frames to wait until moving to the next animation frame.
    
    @type _holdFrameNum:             C{int}
    @ivar _holdFrameNum:             Which numbered frame to stay on when the animation completes.  If -1 the animation will
                                     loop.
    
    @type _playing:                  C{bool}
    @ivar _playing:                  C{True} if the animation is being played, C{False} otherwise.  Mutually exclusive with Paused
                                     and Stopped.
    
    @type _paused:                   C{bool}
    @ivar _paused:                   C{True} if the animation is paused, C{False} otherwise.  Mutually exclusive with Playing
                                     and Stopped.
    
    @type _stopped:                  C{bool}
    @ivar _stopped:                  C{True} if the animation is stopped, C{False} otherwise.  Mutually exclusive with Playing and
                                     Paused.
    
    @type _complete:                 C{bool}
    @ivar _compelte:                 C{True} if the animation has played its last frame, C{False} otherwise.  This means a looping
                                     animation will be marked complete after one cycle.
                                     
    @type _stopOnComplete:           C{bool}
    @ivar _stopOnComplete:           C{True} if the animation should be L{stopped<Animation.Animation.Stop>} after it finishes playing.
    """

    # hold all the loaded sprite sheets so we don't reload them
    loadedSpriteSheets = {}

    def __init__(self, sheetPath, frameRect, totalFrames, frameDelay=0, holdFrame=-1, colorKey=None, alpha=False):
        """
        Creates a new animation by loading the sprite sheet at the given path, and creating frames starting at the given
        rectangle.  Either a color key or alpha can be used for transparency, but not both.
        
        @type  sheetPath:       C{str}
        @param sheetPath:       The path to the location of the sprite sheet file.
        
        @type  frameRect:       U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
        @param frameRect:       Rectangle that describes the position and dimensions of the first frame in the animation.
        
        @type  totalFrames:     C{int}
        @param totalFrames:     Total number of frames in the animation.
        
        @type  frameDelay:      C{int}
        @param frameDelay:      How many frames of the game should pass before switching to the next animation frame.
        
        @type  holdFrame:       C{int}
        @param holdFrame:       Which numbered frame to stay on when the animation completes.  If -1 the animation will
                                loop.
        
        @type  colorKey:        C{U{pygame.Color<http://www.pygame.org/docs/ref/color.html>}}
        @param colorKey:        What color should be considered transparent in the sprite sheet.  C{None} if using a file type with
                                alpha values (like .PNG), or if no color should be transparent.
        
        @type  alpha:           C{bool}
        @param alpha:           C{True} if the sprite sheet file type has alpha values (like .PNG), C{False} otherwise.  This is
                                mutually exclusive with L{colorKey}.
        """
        
        # error check
        if (colorKey and alpha):
            raise Exception('Animation from file "' + sheetPath + '" should not have both colorKey and alpha values set.')
        
        # don't load the image multiple times
        if Animation.loadedSpriteSheets.has_key(sheetPath):
            self._spriteSheet = Animation.loadedSpriteSheets[sheetPath]
        else:
            self._spriteSheet = pygame.image.load(sheetPath)
            Animation.loadedSpriteSheets[sheetPath] = self._spriteSheet
            
            # check transparency
            if alpha:
                self._spriteSheet.convert_alpha()
            else:
                self._spriteSheet.set_colorkey(colorKey)
                self._spriteSheet.convert()
        
        # set up the first frame
        self._startPos = frameRect.topleft
        self._frame = self._spriteSheet.subsurface(frameRect)
        self._frameNum = 0
        self._framesUntilChange = frameDelay
        
        # limits on the animation
        self._totalFrames = totalFrames
        self._frameDelay = frameDelay
        self._holdFrameNum = holdFrame
        
        # set the statuses
        self._complete = False
        self._playing = False
        self._paused = False
        self._stopped = True
        self._stopOnComplete = False

    def GetFrame(self):
        """
        Returns the current frame of animation and moves to the next frame if the animation is being played.
        
        @rtype:            C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @return:           Surface for the current frame of animation.
        """
        frame = self._frame
        
        # keep counting frames if we'll need to move to the next frame (looping or hasn't completed yet)
        if self._playing and self.Looping or not self._complete:
            self._framesUntilChange -= 1
            # waited long enough, move to the next frame
            if self._framesUntilChange < 0:
                self._framesUntilChange = self._frameDelay
                self.__increment_frame__()
        
        return frame
        
    def __increment_frame__(self):
        """
        Moves to the next frame and sets the animation as complete if passing the last frame.
        """
        self._frameNum += 1
        
        # check for completion
        if self._frameNum >= self._totalFrames:
            self._complete = True
            
            # check for loops
            if self._stopOnComplete:
                self.Stop()
            elif self.Looping:
                self._frameNum = 0
            else:
                self._frameNum = self._holdFrameNum
        
        # setup the next frame
        self.__goto_frame__(self._frameNum)
        
    def __goto_frame__(self, frameNum):
        """
        Goes to the given frame and prepares it for drawing.
        
        @type  frameNum:    C{int}
        @param frameNum:    Frame in this animation go to. 
        """
        self._frameNum = frameNum
        self._framesUntilChange = self._frameDelay
        
        frameRect = self._frame.get_rect()
        
        frameRect.x = self._startPos[0] + (frameRect.width * frameNum)
        frameRect.y = self._startPos[1]
        
        try:
            self._frame = self._spriteSheet.subsurface(frameRect)
        except ValueError:
            print 'lolwut'
            
    
    def Play(self, startFrame=None):
        """
        Plays the animation.  Each time L{GetFrame} is called, the animation will track and increment frames.  If paused,
        this resumes the animation.
        
        @type  startFrame:    C{int}
        @param startFrame:    Which numbered frame to begin playing on.  If C{None}, it will either begin playing on
                              frame 0, or if previously paused, it will resume with the last active frame.
        """
        
        # do not restart if we are already playing
        if self.Playing:
            return
        
        # start from the frame and reset delay
        if startFrame != None:
            self.__goto_frame__(startFrame)
            
        self._playing = True
        self._paused = False
        self._stopped = False
    
    def PlayOnce(self, startFrame=None):
        """
        Plays the animation to completion once, then stops.
        """
        self._stopOnComplete = True
        self.Play(startFrame)
    
    def Pause(self):
        """
        Pauses the animation, so that L{GetFrame} will not increment to the next frame, but does not reset the animation.
        """
        if self.Stopped:
            return
        
        self._paused = True
        self._playing = False
        self._stopped = False
    
    def Stop(self):
        """
        Stops the animation, so L{GetFrame} will not increment to the next frame, and also resets the animation. 
        """
        if self.Stopped:
            return
        
        self._stopped = True
        self._playing = False
        self._paused = False
        self._complete = False
        self._stopOnComplete = False
        self.__goto_frame__(0)

    ############### PROPERTIES ###############
            
    def __is_looping__(self):
        return self._holdFrameNum == -1
    def __set_looping__(self, loop):
        if loop:
            self._holdFrameNum = -1
        elif self.Looping:
            self._holdFrameNum = 0
    
    def __get_hold_frame__(self):
        return self._holdFrameNum
    def __set_hold_frame__(self, value):
        self._holdFrameNum = value
        
    def __is_complete__(self):
        return self._complete
    def __is_playing__(self):
        return self._playing
    def __is_paused__(self):
        return self._paused
    def __is_stopped__(self):
        return self._stopped
    
    def __get_frame_num__(self):
        return self._frameNum
    def __set_frame_num__(self, value):
        self.__goto_frame__(value)
        
    def __get_num_animation_frames__(self):
        return self._totalFrames
    def __get_num_total_frames__(self):
        return self._totalFrames * (self._frameDelay + 1)
    
    Looping = property(__is_looping__, __set_looping__, None, "C{True} if the animation should loop, C{False} otherwise.")
    HoldFrameNumber = property(__get_hold_frame__, __set_hold_frame__, None, "Which numbered frame to stay on when the animation is complete.")
    Completed = property(__is_complete__, None, None, "C{True} if the animation has played its last frame, C{False} otherwise.")
    Playing = property(__is_playing__, None, None, "C{True} if the animation is playing, C{False} otherwise.")
    Paused = property(__is_paused__, None, None, "C{True} if the animation is paused, C{False} otherwise.")
    Stopped = property(__is_stopped__, None, None, "C{True} if the animation is stopped, C{False} otherwise.")
    FrameNum = property(__get_frame_num__, __set_frame_num__, None, "The number of the currently active frame of animation.")
    NumAnimationFrames = property(__get_num_animation_frames__, None, None, "The number of animation frames in the animation.")
    LoopLength = property(__get_num_total_frames__, None, None, "The number of render frames it takes to complete one full animation loop.")