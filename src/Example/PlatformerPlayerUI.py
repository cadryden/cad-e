'''
Created on Jun 13, 2010

@author: Chris Alvarado-Dryden
'''

from UI.Panel import Panel
from UI.Meter import Meter
from UI.Box import Box
from UI.Text import Text
from Example.PlatformerTimer import PlatformerTimer
from UI.Textured import Textured
from Core import Constants
import Utilities
from pygame import Color
import pygame
import os

class PlatformerPlayerUI(Panel):
    '''
    classdocs
    '''

    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        
        @type  attrs:     C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:     Attributes of the element.     
        
        @type  basePath:  C{str}                                                       
        @param basePath:  Base file path to be used for resource loading.
        
        @type  map:       L{GameMap<Map.GameMap.GameMap>}
        @param map:       Used to reference objects within the map if the Widget needs to access them.                                                        
        """
        params = []
        
        playerNum = int(attrs.get('player'))
        
        params.append((int(attrs.get('x')), int(attrs.get('y'))))
        params.append(map.Players[playerNum])
        if attrs.has_key('color'):
            colorTup = Utilities.HelperFunctions.StringConversions.StringToIntTuple(str(attrs.get('color')))
            params.append(Color(*colorTup))
        else:
            params.append(Color(255, 255, 255))
        
        return params

    def __init__(self, position, player, color):
        '''
        Constructor
        '''
        
        width = 400
        height = 200
        
        Panel.__init__(self, position, width, height)
        
        self._player = player
        
        self.AddChild(Box((14, 10), 232, 40, Color(200, 200, 200, 100)))
        
        self._throwMeter =  Meter((14, 10), 232, 40, color, lambda: Constants.PlayerConstants.THROW_COOLDOWN - player._throwCoolDown, lambda: Constants.PlayerConstants.THROW_COOLDOWN)
        self.AddChild(self._throwMeter)

        #self._portrait = Box((5, 5), 40, 40, color)
        #self.AddChild(self._portrait)
        
        #smashText = Text((70, 50), '../content/fonts/hulk.ttf', 22, 'ATTACK', color)
        smashText = Text((90, 20), '../content/fonts/upheavtt.ttf', 22, 'ATTACK', Color(0, 0, 0))
        self.AddChild(smashText)
        
        self.AddChild(Textured((10, 10), 300, 40, '../content/gfx/elements/barHolder.png'))
        
    def ToXMLString(self):
        """
        
        """
        typeName = self.__class__.__module__
        
        xmlString = '<panel type="' + typeName + '" '
        xmlString += 'x="'+ self.Position[0].__str__() +'" '
        xmlString += 'y="'+ self.Position[1].__str__() +'" '        
        xmlString += 'player="' + self._player.PlayerNum.__str__() + '" >\n'
        for child in self._children:
            if child is not self._throwMeter:# and child is not self._portrait:
                xmlString += child.ToXMLString()
        xmlString += '</panel>\n'
            
        return unicode(xmlString)