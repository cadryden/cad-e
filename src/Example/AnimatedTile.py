'''
Created on May 7, 2010

@author: Chris Alvarado-Dryden
'''

from Map.GameTile import GameTile
from Core.Animation import Animation
from Core.Sound import Sound
from Utilities.vector import Vector
from Utilities.HelperFunctions import StringConversions 
import os


from Core import Constants

import pygame.rect

class AnimatedTile(GameTile):
    '''
    classdocs
    '''


    def __init__(self, loaderTile, surface, xIndex, yIndex, layer):
        '''
        Constructor
        '''
        
        GameTile.__init__(self, loaderTile, surface, xIndex, yIndex, layer)
        
        #sheetPath, frameRect, totalFrames, frameDelay=0, holdFrame=-1, colorKey=None, alpha=False
        # sheet path, frame size, total frames, frame delay, hold frame, key color 
        sheetPath = os.path.realpath(os.path.join(self.Layer.Map.FilePath, self.properties['sheet path'].strip()))
        
        if self.properties.has_key('frame size') and self.properties['frame size'].strip():
            frameSize = StringConversions.StringToIntTuple(self.properties['frame size'])
        else:
            frameSize = (self.Width, self.Height)
        frameRect = pygame.Rect((0, 0), frameSize)
            
        totalFrames = int(self.properties['total frames'])
        
        if self.properties.has_key('frame delay') and self.properties['frame delay'].strip():
            frameDelay = int(self.properties['frame delay'])
        else:
            frameDelay = 0
            
        if self.properties.has_key('hold frame') and self.properties['hold frame'].strip():
            # in editor, things are 1 based
            holdFrame = int(self.properties['hold frame']) - 1
        else:
            holdFrame = -1
            
        if self.properties.has_key('key color') and self.properties['key color'].strip():
            keyColor = pygame.Color(StringConversions.StringToIntTuple(self.properties['key color']))
            alpha = False
        else:
            keyColor = None
            alpha = True
        
        if self.properties.has_key('offset') and self.properties['offset'].strip():
            offset = StringConversions.StringToIntTuple(self.properties['offset'])
        else:
            offset = (0, 0)
            
        anim  = Animation(sheetPath, frameRect, totalFrames, frameDelay, holdFrame, keyColor, alpha)
        self._animations['anim'] = anim
        self._drawOffsets[anim] = Vector(offset)
        
        # tile test animation
        """
        anim = Animation('../resources/tiles/tile_arrow_anim.png', pygame.Rect(0, 0, 32, 32), 3, 9, -1, None, True)
        self._animations['up'] = anim
        self._drawOffsets[anim] = Vector((0, 0))
        
        anim2 = Animation('../resources/tiles/tile_arrow_anim.png', pygame.Rect(0, 0, 32, 32), 3, 0, 0, None, True)
        self._animations['bounce'] = anim2
        self._drawOffsets[anim2] = Vector((0, 0))
        """

        self._sounds['bounce'] = Sound('../content/sounds/boing.ogg', Constants.GameConstants.SOUND_VOLUME)
        
        self.PlayAnimation('anim')
    
    def ResolveCollision(self, other):
        #other.Visible = not other.Visible
        #self.PlayAnimation('bounce')
        self.PlaySound('bounce')
        #self.QueueAnimation('up')
        return
        