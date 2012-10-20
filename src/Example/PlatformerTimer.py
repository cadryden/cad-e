"""
Created on Jun 17, 2010

@author: Chris Alvarado-Dryden
"""

import UI, Utilities
import os, pygame

class PlatformerTimer(UI.Text.Text):
    """
    A text count up/down timer.
    """
    @staticmethod
    def AttributesToParameters(attrs, basePath, map):

        fontPath = attrs.get('font')
        if '.' in fontPath:
            fontPath = os.path.normpath(os.path.realpath(os.path.join(basePath, fontPath)))
        
        fontSize = int(attrs.get('size'))
        startTime = float(attrs.get('start'))
        
        startStr = attrs.get('start')
        startStr.strip()
        if '.' in startStr:
            # number of digits after decimal point
            sep = startStr.split('.', 1)
            leading = len(sep[0])
            decimals = len(sep[1])
        else:
            leading = len(startStr)
            decimals = 0
        
        if attrs.get('direction') == 'down':
            countUp = False
        else:
            countUp = True
            
        if (attrs.has_key('color')):
            color = attrs.get('color')
            color = Utilities.HelperFunctions.StringConversions.StringToIntTuple(color)
            color = pygame.Color(color[0], color[1], color[2])
        else:
            color = None
        
        if attrs.has_key('bgColor'):
            bgColor = attrs.get('bgColor')
            bgColor = Utilities.HelperFunctions.StringConversions.StringToIntTuple(bgColor)
            bgColor = pygame.Color(bgColor[0], bgColor[1], bgColor[2])
        else:
            bgColor = None
        
        params = []
        params.append((int(attrs.get('x')), int(attrs.get('y'))))  
        params.append(fontPath)
        params.append(fontSize)
        params.append(startTime)
        params.append(countUp)
        params.append(leading)
        params.append(decimals)
        params.append(color)
        params.append(bgColor)
        
        return params

    def __init__(self, position, fontPath, fontSize, startTime, countUp, leading=2, decimals=2, fontColor=None, fontBGColor=None):
        """
        
        """
        
        UI.Text.Text.__init__(self, position, fontPath, fontSize, str(startTime), fontColor, fontBGColor)
        
        self.Time = startTime
        self._startTime = startTime
        self._countUp = countUp
        self._leading = leading
        self._decimals = decimals
        
    def Update(self, dt):
        """
        
        """
        if self._countUp:
            self.Time += dt
        else:
            self.Time -= dt

        # truncate the time instead of rounding it
        s = str(self.Time)
        s = self.__format_float__(s, self._leading, self._decimals)
        
        self.Text = s
            
    def ToXMLString(self):
        """
        
        """
        color = (self._fontColor.r, self._fontColor.g, self._fontColor.b, self._fontColor.a)
        if self._fontBGColor:
            bgColor = (self._fontBGColor.r, self._fontBGColor.g, self._fontBGColor.b, self._fontBGColor.a).__str__()
        else:
            bgColor = 'None'
        
        typeName = self.__class__.__module__
        
        xmlString = '<widget type="' + typeName + '" '
        xmlString += 'x="'+ self.Position[0].__str__() +'" '
        xmlString += 'y="'+ self.Position[1].__str__() +'" '
        
        if '.' in self._fontPath:
            xmlString += 'font="' + os.path.basename(self._fontPath) + '" '
        else:
            xmlString += 'font="' + self._fontPath + '" '
        xmlString += 'size="' + self._fontSize.__str__() + '" '
        xmlString += 'start="' + self.__format_float__(str(self._startTime), self._leading, self._decimals) + '" '
        
        if self._countUp:
            xmlString += 'direction="up" '
        else:
            xmlString += 'direction="down" '
            
        xmlString += 'color="' + color.__str__() + '" '
        xmlString += 'bgColor="' + bgColor + '" '
        xmlString += '/>\n'
        
        return xmlString
    
    def __format_float__(self, num, leading, decimals):
        """
        
        """
        i,d = num.split('.')
        
        i = i.zfill(leading)
        d = d[:decimals]
        if (len(d) < decimals):
            for n in range(decimals - len(d)):
                d += '0'
        
        if decimals <= 0:
            s = i
        else:
            s = i + '.' + d
            
        return s
