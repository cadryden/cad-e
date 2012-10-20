'''
Created on Aug 3, 2010

@author: F642390
'''

from Example.PlatformerMenuButton import PlatformerMenuButton
from UI.Text import Text
from UI.Menu.MenuButton import MenuButton


class PlatformerPlayMenuButton(PlatformerMenuButton):
    '''
    classdocs
    '''

    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        
        """
        
        params = []
        
        params.append(attrs.get('name'))
        
        params.extend(Text.AttributesToParameters(attrs, basePath, map))
        
        # menu
        params.append(None)
        
        # only get neighbors, which is the last item
        params.append(MenuButton.AttributesToParameters(attrs, basePath, map)[-1])
        
        return params

    def __init__(self, name, position, fontPath, fontSize, text, fontColor, fontBGColor, menu=None, neighbors=None):
        '''
        Constructor
        '''
        PlatformerMenuButton.__init__(self, name, None, position, fontPath, fontSize, text, fontColor, fontBGColor, menu, neighbors)
        
    def OnSelect(self):
        PlatformerMenuButton.OnSelect(self)
        
        if self._menu.Name == 'Main Menu' or not self._menu.Game.CurrentMap:
            self._menu.Game.PlayMap(0)
        else:
            self._menu.Game.PlayMap(self._menu.Game.CurrentMap.FileName)

        """
        if self._menu.Game.CurrentMap:
            self._menu.Game.PlayMap(self._menu.Game.CurrentMap.FileName)
        else:
            self._menu.Game.PlayMap(0)
        """