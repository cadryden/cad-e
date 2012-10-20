'''
Created on Aug 2, 2010

@author: F642390
'''

import UI
from Core.MusicPlayer import MusicPlayer

from UI.Meter import Meter
from UI.Box import Box
from UI.Text import Text
from PlatformerFunctionMenuButton import PlatformerFunctionMenuButton
from Core import Constants
from pygame import Color
import pygame
import os

from Example.PlatformerMenu import PlatformerMenu

class PlatformerVolumeMenu(PlatformerMenu):
    '''
    classdocs
    '''
    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        
        params = []
        
        params.append(attrs.get('name'))
        
        x = int(attrs.get('x'))        
        y = int(attrs.get('y'))
        params.append((x,y))
        
        
        params.append(int(attrs.get('width')))
        
        
        params.append(int(attrs.get('height')))
        
        return params

    def __init__(self, name, position, width, height):
        '''
        Constructor
        '''
        
        #position = (410, 280)
        #width = 400
        #height = 600
        
        PlatformerMenu.__init__(self, name, position, width, height)
        

        # music
        meterPos = (20, 40)
        meterWidth = 320
        meterHeight = 25
        
        self._meterBack = Box(meterPos, meterWidth, meterHeight, Color(0, 0, 0))
        self.AddChild(self._meterBack)
        self._meter = Meter(meterPos, meterWidth, meterHeight, Color(255, 255, 255), pygame.mixer.music.get_volume, lambda: 1.0)
        self.AddChild(self._meter)
        
        fontPath = os.path.join(Constants.GameConstants.BASE_PATH, 'content/fonts/upheavtt.ttf')
        
        self._musicText = Text((140, 0), fontPath, 32, 'MUSIC', Color(0, 255, 0))
        self.AddChild(self._musicText)
        
        self._musicMinus = PlatformerFunctionMenuButton('Music Minus', self.__decrementMusic__, (-5, 38), fontPath, 32, '-', Color(0, 255, 0), None)
        self.AddChild(self._musicMinus)
        

        self._musicPlus = PlatformerFunctionMenuButton('Music Plus', self.__incrementMusic__, (350, 35), fontPath, 32, '+', Color(0, 255, 0), None)        
        self.AddChild(self._musicPlus)
        
        
        # sound effects
        meterPos = (20, 110)
        meterWidth = 320
        meterHeight = 25
        
        self._meterBack = Box(meterPos, meterWidth, meterHeight, Color(0, 0, 0))
        self.AddChild(self._meterBack)
        self._meter = Meter(meterPos, meterWidth, meterHeight, Color(255, 255, 255), lambda: Constants.GameConstants.SOUND_VOLUME, lambda: 1.0)
        self.AddChild(self._meter)
        
        
        self._soundText = Text((140, 70), fontPath, 32, 'SOUND', Color(0, 255, 0))
        self.AddChild(self._soundText)
        
        self._soundMinus = PlatformerFunctionMenuButton('Sound Minus', self.__decrementSound__, (-5, 108), fontPath, 32, '-', Color(0, 255, 0), None)
        self.AddChild(self._soundMinus)
        

        self._soundPlus = PlatformerFunctionMenuButton('Sound Plus', self.__incrementSound__, (350, 105), fontPath, 32, '+', Color(0, 255, 0), None)        
        self.AddChild(self._soundPlus)
        
        
        
        # navigation
        self._musicMinus.RightNeighborName = self._musicPlus.Name
        self._musicMinus.BelowNeighborName = self._soundMinus.Name
        
        self._musicPlus.LeftNeighborName = self._musicMinus.Name
        self._musicPlus.BelowNeighborName = self._soundPlus.Name
        
        self._soundMinus.RightNeighborName = self._soundPlus.Name
        self._soundMinus.AboveNeighborName = self._musicMinus.Name
        
        self._soundPlus.LeftNeighborName = self._soundMinus.Name
        self._soundPlus.AboveNeighborName = self._musicPlus.Name
        
    @staticmethod
    def __decrementMusic__():
        MusicPlayer().Volume -= 0.1
        
        
    @staticmethod
    def __incrementMusic__():
        MusicPlayer().Volume += 0.1
        
    @staticmethod
    def __decrementSound__():
        newVol = Constants.GameConstants.SOUND_VOLUME - 0.1
        Constants.GameConstants.SOUND_VOLUME = max(min(1.0, newVol), 0.0)
        
        
    @staticmethod
    def __incrementSound__():
        newVol = Constants.GameConstants.SOUND_VOLUME + 0.1
        Constants.GameConstants.SOUND_VOLUME = max(min(1.0, newVol), 0.0)
        
        
    def ToXMLString(self):
        """
        Generates XML to create this Menu.
        
        Suppress children XML
        
        @rtype:        C{unicode}
        @return:       XML that can be read back through the XML parser.
        """
        xmlString = UI.Panel.Panel.__begin_typed_xml_string__(self)
        xmlString += 'name="' + self.Name + '" '
        
        xmlString += '>\n'
                
        xmlString += '</panel>'
        return unicode(xmlString)
        

