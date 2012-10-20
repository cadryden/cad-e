'''
Created on Sep 30, 2010

@author: F642390
'''

from Example.PlatformerMenuButton import PlatformerMenuButton
from UI.Text import Text
from UI.Menu.MenuButton import MenuButton


class PlatformerLevelSelectMenuButton(PlatformerMenuButton):
    '''
    classdocs
    '''

    def __init__(self, name, targetMapName, position, fontPath, fontSize, text, fontColor, fontBGColor, menu=None, neighbors=None):
        '''
        Constructor
        '''
        PlatformerMenuButton.__init__(self, name, None, position, fontPath, fontSize, text, fontColor, fontBGColor, menu, neighbors)
        
        self._switchToMap = False
        
        self._targetMapName = targetMapName
        self._switchDelay = 1
        
    def OnSelect(self):
        self._fontColor = self._selectColor
        self.__build_surface__()
        self._switchToMap = True

    def Update(self, dt):
        if self._switchToMap:
            self._switchDelay -= 1
            if self._switchDelay < 0:
                self._menu.Game.PlayMap(self._targetMapName)
                PlatformerMenuButton.OnSelect(self)
                
                self._switchToMap = False
                self._switchDelay = 1