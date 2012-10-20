"""
A widget to display text on the screen.

@author: Chris Alvarado-Dryden
"""
import os
import pygame
import Utilities
from Core import Constants
from UI.Widget import Widget

class Text(Widget):
    """
    A widget to display text on the screen.
    
    The Text widget's width and height are determined by the text itself, not by the Widget's attributes.
    Alpha values will only be read for the text (not the background) but applied to both.
    
    @type _rect:          U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar _rect:          The dimensions and position of the Widget in pixels.  The position is
                          relative to its parent's position.
    
    @type _parent:        L{Panel<UI.Panel.Panel>}
    @ivar _parent:        The Panel this Widget belongs to.
    
    @type _image:         U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _image:         Image to draw to the screen.
    
    @type _fontPath:      C{str}
    @ivar _fontPath:      File path to the chosen appropriate font.  If it is a system font, only the name
                          is needed, such as C{'Courier New'}, otherwise it is a relative path.
    
    @type _font:          U{C{pygame.Font}<http://www.pygame.org/docs/ref/font.html#pygame.font.Font>}
    @ivar _font:          pygame Font object used to render the text.
    
    @type _fontColor:     U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _fontColor:     The color of the font.  If C{None} the font will be black.
    
    @type _fontBGColor:   U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _fontBGColor:   The background color of the text.  If C{None} it will be clear.
    
    @type _fontSize:      C{int}
    @ivar _fontSize:      Size of the font.
    
    @type Visible:        C{bool}
    @ivar Visible:        C{True} if the Widget should be drawn, C{False} otherwise.
    
    @type Text:           C{str}
    @ivar Text:           Text that should be displayed.  Newline characters will be ignored.
    
    """
    @staticmethod
    def AttributesToParameters(attrs, basePath, map):
        """
        Takes the values of the passed in dictionary then maps and arranges them into an appropriate
        parameter list for object construction.  It looks for the following attributes:
        
            - C{x}
            - C{y}
            - C{font}
            - C{size}
            - C{text}
            - C{color}
            - C{bgColor}
        
        @type  attrs:     C{U{Attributes<http://docs.python.org/library/xml.sax.reader.html#attributes-objects>}}
        @param attrs:     Attributes of the element.
        
        @type  basePath:  C{str}                                                       
        @param basePath:  Base file path to be used for resource loading.
        
        @type  map:       L{GameMap<Map.GameMap.GameMap>}
        @param map:       Used to reference objects within the map if the Widget needs to access them.
        
        @rtype:           C{list}
        @return:          Values of the attributes to be used as parameters, in parameter list order for the constructor.    
        """
        fontPath = attrs.get('font')
        if '.' in fontPath:
            fontPath = os.path.normpath(os.path.realpath(os.path.join(basePath, fontPath)))
        
        fontSize = int(attrs.get('size'))
        text = attrs.get('text')
        
        colorTup = attrs.get('color')
        colorTup = Utilities.HelperFunctions.StringConversions.StringToIntTuple(colorTup)
        color = pygame.Color(colorTup[0], colorTup[1], colorTup[2])
        if len(colorTup) > 3:
            color.a = colorTup[3]
        
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
        params.append(text)
        params.append(color)
        params.append(bgColor)
        
        return params
        
    def __init__(self, position, fontPath, fontSize, text, fontColor=None, fontBGColor=None):
        """
        Creates a new Text UI widget at the given position, and with the given text attributes.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  fontPath:        C{str}
        @param fontPath:        File path to the chosen font.  If it is a system font, only the name
                                is needed, such as C{'Courier New'}, otherwise it should be an absolute path.
        
        @type  fontSize:        C{int}
        @param fontSize:        Size of the font.
        
        @type  text:            C{str}
        @param text:            Text that should be displayed.  Newline characters will be ignored.
        
        @type  fontColor:       U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
        @param fontColor:       The color of the font.  If C{None} the font will be black.
        
        @type  fontBGColor:     U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
        @param fontBGColor:     The background color of the text.  If C{None} it will be clear.
        """
        Widget.__init__(self, position, 1, 1)
        
        self._fontPath = fontPath
        self.Text = text
        self._fontSize = fontSize
        
        if not os.path.exists(fontPath):
            self._font = pygame.font.SysFont(fontPath, fontSize)
        else:
            fontPath = os.path.normpath(os.path.realpath(fontPath))
            self._font = pygame.font.Font(fontPath, fontSize)
            
            # reset font path to relative for output
            self._fontPath = fontPath.lstrip(os.path.normpath(os.path.realpath(Constants.GameConstants.BASE_PATH)))

        if not fontColor:
            self._fontColor = pygame.Color(0, 0, 0)
        else:
            self._fontColor = fontColor
        
        self._fontBGColor = fontBGColor
        
        self.__build_surface__()
        
    def __build_surface__(self):
        """
        Renders the font to the L{_image} surface so it can be drawn.
        """
        # pygame doc not accurate.  Can't pass None as last argument
        # could optimize by putting this in constructor and storing surface
        if self._fontBGColor:
            fontSurf = self._font.render(self.Text, True, self._fontColor, self._fontBGColor)
        else:
            fontSurf = self._font.render(self.Text, True, self._fontColor)
            
        self._image = fontSurf
        self._image.convert_alpha()
        if self._fontColor.a < 255:
            self._image.set_alpha(self._fontColor.a)
        
        self._rect.w = self._image.get_width()
        self._rect.h = self._image.get_height()
        
    def DrawTo(self, surf):
        """
        Draws the text to the given Surface if its visible.  If the Widget is not completely within
        its parent's panel, it will be clipped.
        
        @type  surf:        C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @param surf:        Surface to draw this Widget to.
        """

        self.__build_surface__()
        Widget.DrawTo(self, surf)
        
    def ToXMLString(self):
        """
        Generates XML to create this Widget.
        
        Ex:
        
        C{<widget type="UI.Text" x="100" y="100" font="../content/fonts/font.ttf" size="72" text="Hello World" color="(255, 0, 0, 255)" />}
        
        or
        
        C{<widget type="UI.Text" x="100" y="100" font="Arial" size="72" text="Hello World" color="(255, 0, 0, 255)" />}
        
        @rtype:        C{unicode}
        @return:       XML that can be read back through the XML parser.
        """
        color = (self._fontColor.r, self._fontColor.g, self._fontColor.b, self._fontColor.a)
        if self._fontBGColor:
            bgColor = (self._fontBGColor.r, self._fontBGColor.g, self._fontBGColor.b, self._fontBGColor.a).__str__()
        
        typeName = self.__class__.__module__
        
        xmlString = '<widget type="' + typeName + '" '
        xmlString += 'x="'+ self.Position[0].__str__() +'" '
        xmlString += 'y="'+ self.Position[1].__str__() +'" '
        xmlString += 'font="' + self._fontPath + '" '
        xmlString += 'size="' + self._fontSize.__str__() + '" '
        xmlString += 'text="' + self.Text + '" '
        xmlString += 'color="' + color.__str__() + '" '
        
        if self._fontBGColor:
            xmlString += 'bgColor="' + bgColor + '" '
        
        xmlString += '/>\n'
        
        return xmlString
        