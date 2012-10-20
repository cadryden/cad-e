'''
Created on May 7, 2010

@author: Chris Alvarado-Dryden
'''

from Map.GameTile import GameTile
from Core.Animation import Animation
from Core.Sound import Sound
from Utilities.vector import Vector
from Utilities.HelperFunctions import StringConversions 


from Core import Constants

import pygame.rect

class BounceTile(GameTile):
    '''
    classdocs
    '''


    def __init__(self, loaderTile, surface, xIndex, yIndex, layer):
        '''
        Constructor
        '''
        
        GameTile.__init__(self, loaderTile, surface, xIndex, yIndex, layer)
        
        # ghetto add config from editor
        # note only Y is used
         
        if self.properties.has_key('velocity') and self.properties['velocity'].strip():
            self.BounceVelocity = Vector((0, int(self.properties['velocity'])))
        else:
            self.BounceVelocity = Vector((0, -850))
        
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
        
        #self.PlayAnimation('up')
    
    def ResolveCollision(self, other):
        #other.Visible = not other.Visible
        #self.PlayAnimation('bounce')
        self.PlaySound('bounce')
        #self.QueueAnimation('up')
        return
        