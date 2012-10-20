'''
Created on Jan 13, 2010

@author: Chris Alvarado-Dryden
'''

from Core import Constants
from Example.PlatformerGame import PlatformerGame
import os

def main():
    """
    loop, if MapComplete, change map

    @todo:    openGL
    @todo:    Timed / other SpawnPoints
    @todo:    Map goals?
    @todo:    directional input change
    """
    
    iconPath = '../content/gfx/elements/cadIcon32.png'
    if not os.path.isfile(os.path.abspath(iconPath)):
        iconPath = None
    game = PlatformerGame('Cuboid Clash', iconPath, Constants.GameConstants.WINDOW_WIDTH, Constants.GameConstants.WINDOW_HEIGHT, 30, openGLMode=False)
    

    game.Run()
    
    print 'exiting'
    return

if __name__ == '__main__':
    main()