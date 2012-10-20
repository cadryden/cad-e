'''
Created on Jul 4, 2010

@author: F642390
'''

from UI.Text import Text
from UI.Menu.MenuButton import MenuButton

import pygame

class PlatformerMenuButton(Text, MenuButton):
    """
    
    Additional variables:
    
    @type _defaultColor:            U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _defaultColor:
    
    @type _highlightColor:            U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _highlightColor:
    
    @type _selectColor:             U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _selectColor:
    
    @type _targetMenuName:          C{str}
    @ivar _targetMenuName:
    
    """

    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        
        """
        
        params = []
        
        params.append(attrs.get('name'))
        if attrs.has_key('target'):
            params.append(attrs.get('target'))
        else:
            params.append(None)
        
        params.extend(Text.AttributesToParameters(attrs, basePath, map))
        
        # menu
        params.append(None)
        
        # only get neighbors, which is the last item
        params.append(MenuButton.AttributesToParameters(attrs, basePath, map)[-1])
        
        return params

    def __init__(self, name, targetMenuName, position, fontPath, fontSize, text, fontColor, fontBGColor, menu=None, neighbors=None):
        '''
        Constructor
        '''
        MenuButton.__init__(self, position, 1, 1, name, menu, neighbors)
        Text.__init__(self, position, fontPath, fontSize, text, fontColor, fontBGColor)
        
        self._defaultColor = self._fontColor
        self._highlightColor = pygame.Color(255, 255, 255)
        self._selectColor = pygame.Color(255, 255, 0)
        self._targetMenuName = targetMenuName
        
    def OnHighlight(self):
        """
        
        """
        self._fontColor = self._highlightColor
        self.__build_surface__()
        
    def OnDeHighlight(self):
        """
        
        """
        self._fontColor = self._defaultColor
        self.__build_surface__()
        
    def OnSelect(self):
        """
        
        """
        self._fontColor = self._selectColor
        self.__build_surface__()
        self._menu.Game.TransitionToMenu(self._targetMenuName)
        
    def ToXMLString(self):
        """
        
        """
        xmlString = MenuButton.ToXMLString(self)
        xmlString = xmlString.rstrip('/>\n')
        
        if self._targetMenuName:
            xmlString += 'target="' + self._targetMenuName + '" '
        
        color = (self._defaultColor.r, self._defaultColor.g, self._defaultColor.b, self._defaultColor.a)
        if self._fontBGColor:
            bgColor = (self._fontBGColor.r, self._fontBGColor.g, self._fontBGColor.b, self._fontBGColor.a).__str__()
        else:
            pass
            #bgColor = 'None'
        
        xmlString += 'font="' + self._fontPath + '" '
        xmlString += 'size="' + self._fontSize.__str__() + '" '
        xmlString += 'text="' + self.Text + '" '
        xmlString += 'color="' + color.__str__() + '" '
        
        if self._fontBGColor:
            xmlString += 'bgColor="' + bgColor + '" '
        
        xmlString += '/>\n'
        
        return xmlString