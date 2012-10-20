'''
Created on Sep 24, 2010

@author: F642390
'''

import UI
from Example.PlatformerMenu import PlatformerMenu
import pygame, os
from Core import Constants

class PlatformerPauseMenu(PlatformerMenu):
    
    def __init__(self, name, position=None, width=None, height=None):
        
        PlatformerMenu.__init__(self, name, position, width, height)
        
        bgWidget = UI.Box.Box(position, width, height, pygame.Color(0, 0, 0, 0))
        self.AddChild(bgWidget)
    
    def OnEnter(self):
        self.Game.CurrentMap.PauseSounds()
        
        UI.Menu.Menu.Menu.OnEnter(self)
    
    def Update(self, dt):
        PlatformerMenu.Update(self, dt)
        
        for controller in self.Controllers:
            if controller.HasButton('Pause') and controller.Button('Pause').Pressed:
                # unpause
                self.Game.TransitionToMenu(None)
                break
    
    def OnExit(self):
        self.Game.CurrentMap.ResumeSounds()
    
    def __get_background__(self):
        return self._children[0]._image
        
    def __set_background__(self, value):
        self._children[0]._image = value
        
    Background = property(__get_background__, __set_background__, None, "Background (previous frame) for the pause menu.")