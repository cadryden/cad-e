'''
A horizontal meter/bar that fills depending on two functions called every frame.

@author: Chris Alvarado-Dryden
'''

from UI.Box import Box
import pygame

class Meter(Box):
    """
    A horizontal meter/bar that fills depending on two functions called every frame.  Note that this UI element
    B{cannot} be read from or written to XML.  In order to use it with XML, include it in another element
    which can provide it with the current and maximum functions.  See
    L{Example.PlatformerPlayerUI<Example.PlatformerPlayerUI.PlatformerPlayerUI>}.
    
    @type _rect:          U{C{pygame.Rect}<http://www.pygame.org/docs/ref/rect.html>}
    @ivar _rect:          The dimensions and position of the Widget in pixels.  The position is
                          relative to its parent's position.
    
    @type _parent:        L{Panel<UI.Panel.Panel>}
    @ivar _parent:        The Panel this Widget belongs to.
    
    @type _image:         U{C{pygame.Surface}<http://www.pygame.org/docs/ref/surface.html>}
    @ivar _image:         Image to draw to the screen.
    
    @type Visible:        C{bool}
    @ivar Visible:        C{True} if the Widget should be drawn, C{False} otherwise.
    
    @type _color:         U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
    @ivar _color:         The color of the meter.
    
    @type _max:           C{float}
    @ivar _max:           Current maximum amount the meter should be filled.
    
    @type _maxFunc:       C{func}
    @ivar _maxFunc:       Function used to get the ratio of current value / maximum value.
    
    @type _amount:        C{float}
    @type _amount:        Current amount the meter should be filled.
    
    @type _amountFunc:    C{func}
    @ivar _amountFunc:    Function used to get the ratio of current value / maximum value.
    """

    def __init__(self, position, width, height, color, amountFunc, maxFunc):
        """
        Creates a new Widget, with the given position, width, height, color, and funtions used to determine
        how far the meter should be filled at a given time.
        
        @type  position:        C{(int, int)}
        @param position:        Position of the Widget in pixels, relative to its parent.
        
        @type  width:           C{int}
        @param width:           Width of the Widget.
        
        @type  height:          C{int}
        @param height:          Height of the Widget.
        
        @type  color:           U{C{pygame.color}<http://www.pygame.org/docs/ref/color.html>}
        @param color:           The color of the Box.
        
        @type  amountFunc:      C{func}
        @param amountFunc:      Function used to get the current amount the meter should be filled.  Should
                                return a positive number.
        
        @type  maxFunc:         C{func}
        @param maxFunc:         Function used to get the maximum amount the meter should be filled.  Should
                                return a positive number.
        """
        Box.__init__(self, position, width, height, color)
        
        self._maxFunc = maxFunc
        self._amountFunc = amountFunc
        
        self._max = self._maxFunc()
        self._amount = self._amountFunc()
        
    def Update(self, dt):
        """
        Updates how much the bar should currently be filled.
        
        @type  dt:        C{float}
        @param dt:        Time in seconds since the last frame refresh.
        """
        self._max = self._maxFunc()
        self._amount = self._amountFunc()
        
    def DrawTo(self, surf):
        """
        Draws the amount of the meter currently filled to the given Surface if its visible.  If the Widget is not
        completely within its parent's panel, it will be clipped.
        
        @type  surf:        C{U{pygame.Surface<http://www.pygame.org/docs/ref/surface.html>}}
        @param surf:        Surface to draw this Widget to.
        """
        percentFill = min(float(self._amount) / float(self._max), 1.0)
        self._image = pygame.Surface((self._rect.width * percentFill, self._rect.height))
        self._image.fill(self.Color)
        
        Box.DrawTo(self, surf)
