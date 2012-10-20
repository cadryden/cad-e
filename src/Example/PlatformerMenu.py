'''
Created on Aug 2, 2010

@author: Chris Alvarado-Dryden
'''

import UI.Menu
from Core import Constants

class PlatformerMenu(UI.Menu.Menu.Menu):
    '''
    classdocs
    '''


    def __init__(self, name, position=None, width=None, height=None):
        '''
        Constructor
        '''
        UI.Menu.Menu.Menu.__init__(self, name, position, width, height)
        
    def OnEnter(self):
        """
        On entry, stop all sounds (specifically for going from Pause to Main Menu)
        """
        if self.Game.CurrentMap:
            self.Game.CurrentMap.StopSounds()
            
        UI.Menu.Menu.Menu.OnEnter(self)
        
    def ProcessInput(self):
        """
        Processes the input from the L{Controllers}.
        """
        for controller in self.Controllers:
            if controller.dpad and self._currentButton:
                nextButton = None
                
                # check up
                if controller.dpad.Up.Pressed:
                    if self._currentButton.AboveNeighborName:
                        nextButton = self._buttons[self._currentButton.AboveNeighborName]
                
                # check down
                if controller.dpad.Down.Pressed:
                    if self._currentButton.BelowNeighborName:
                        nextButton = self._buttons[self._currentButton.BelowNeighborName]
                    
                # check left
                if controller.dpad.Left.Pressed:
                    if self._currentButton.LeftNeighborName:
                        nextButton = self._buttons[self._currentButton.LeftNeighborName]
                        
                # check right
                if controller.dpad.Right.Pressed:
                    if self._currentButton.RightNeighborName:
                        nextButton = self._buttons[self._currentButton.RightNeighborName]
                    
                # switch buttons maybe
                if nextButton:
                    self._currentButton.OnDeHighlight()
                    self._currentButton = nextButton
                    self._currentButton.OnHighlight()

                # check a 'select' button
                if controller.Button('Throw').Pressed:
                    self._currentButton.OnSelect()
                    
                # check a 'back' button
                if controller.Button('Back').Pressed:
                    self.Game.TransitionToMenu(self._prevMenu.Name)