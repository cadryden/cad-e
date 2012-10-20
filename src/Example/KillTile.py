'''
Created on Sep 21, 2010

@author: Chris Alvarado-Dryden
'''

from Map.GameTile import GameTile
from Core.Animation import Animation
from Core.Sound import Sound
from Utilities.vector import Vector
from Utilities.HelperFunctions import StringConversions 

from Core import Constants

import pygame.rect

class KillTile(GameTile):
    '''
    classdocs
    '''


    def __init__(self, loaderTile, surface, xIndex, yIndex, layer):
        '''
        Constructor
        '''
        
        GameTile.__init__(self, loaderTile, surface, xIndex, yIndex, layer)
        
        # tile test animation
        
        """
        anim = Animation('../resources/tiles/tile_arrow_anim.png', pygame.Rect(0, 0, 32, 32), 3, 9, -1, None, True)
        self._animations['up'] = anim
        self._drawOffsets[anim] = Vector((0, 0))
        
        anim2 = Animation('../resources/tiles/tile_arrow_anim.png', pygame.Rect(0, 0, 32, 32), 3, 0, 0, None, True)
        self._animations['bounce'] = anim2
        self._drawOffsets[anim2] = Vector((0, 0))

        self._sounds['bounce'] = Sound('../resources/sounds/boing.ogg', Constants.GameConstants.SOUND_VOLUME)
        
        self.PlayAnimation('up')
        """
        respawnTuple = StringConversions.StringToIntTuple(self.properties['respawn'])
        
        if self.properties.has_key('unit') and self.properties['unit'] == 'pixel':
            # respawnPos is pixels, so keep it
            self._respawnPos = respawnTuple 
        else:
            # convert from tile coords to pixels
            # this is kinda ghetto
            self._respawnPos = (respawnTuple[0] * self.Width, respawnTuple[1] * self.Height)
                
        
        if self.properties.has_key('facing') and self.properties['facing'] == 'right':
            self._respawnRight = True
        else:
            self._respawnRight = False 
    
    def ResolveCollision(self, other):
        #other.Visible = not other.Visible
        """
        self.PlayAnimation('bounce')
        self.PlaySound('bounce')
        self.QueueAnimation('up')
        """
        other.RespawnPosition = self._respawnPos
        other.RespawnFacingRight = self._respawnRight
        other.ChangeState('dead')
        return