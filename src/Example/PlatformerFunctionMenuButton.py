'''
Created on Aug 3, 2010

@author: F642390
'''

from UI.Menu.MenuButton import MenuButton
from UI.Text import Text
import pygame

class PlatformerFunctionMenuButton(Text, MenuButton):
    
    def __init__(self, name, func, position, fontPath, fontSize, text, fontColor, fontBGColor, menu=None, neighbors=None):
        
        MenuButton.__init__(self, position, 1, 1, name, menu, neighbors)
        Text.__init__(self, position, fontPath, fontSize, text, fontColor, fontBGColor)
        
        self._defaultColor = self._fontColor
        self._highlightColor = pygame.Color(255, 255, 255)
        self._selectColor = pygame.Color(255, 255, 0)
        
        self._function = func
        
    def OnHighlight(self):
        """
        
        """
        self._fontColor = self._highlightColor
        self.__build_surface__()
        
    def OnSelect(self):
        """
        
        """
        self._fontColor = self._selectColor
        self.__build_surface__()
        self._function()
        
    def OnDeHighlight(self):
        """
        
        """
        self._fontColor = self._defaultColor
        self.__build_surface__()