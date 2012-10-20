'''
Created on May 19, 2010

@author: Chris Alvarado-Dryden
'''

from Map.GameTile import GameTile
from Core.Animation import Animation
from Utilities.vector import Vector

import pygame.rect

class ExitTile(GameTile):
    '''
    classdocs
    '''


    def __init__(self, loaderTile, surface, xIndex, yIndex, layer):
        '''
        Constructor
        '''
        
        GameTile.__init__(self, loaderTile, surface, xIndex, yIndex, layer)
    
    def ResolveCollision(self, other):
        return
        