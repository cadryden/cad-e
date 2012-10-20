'''
@author: Chris Alvarado-Dryden
'''
import os
import pygame
from Core.Game import Game
from Core import Constants
from Example.PlatformerLevelSelectMenuButton import PlatformerLevelSelectMenuButton

class PlatformerGame(Game):
    """
    An example Game class for a platformer, specifically Cuboid Clash, the CAD-E demo game.
    """

    def CheckPause(self):
        """
        Checks each L{Controller<Utilities.Controller.Controller.Controller>} for the I{pause} button, and transfers to the
        I{pause} L{Menu<UI.Menu.Menu.Menu>} if it is pressed.
        """
        for controller in self.Controllers:
                    if controller.HasButton(Constants.ControllerConstants.PAUSE_BUTTON) and controller.Button(Constants.ControllerConstants.PAUSE_BUTTON).Pressed:
                        self.TransitionToMenu(Constants.MenuCosntants.PAUSE_MENU_NAME)
                        self._menuDict[Constants.MenuCosntants.PAUSE_MENU_NAME].Background = pygame.display.get_surface().copy()
                        
    def CheckMapEnd(self):
        """
        Checks if one of the L{PlatformerPlayer<Example.PlatformerPlayer.PlatformerPlayer>}s has won and shows the I{retry}
        L{Menu<UI.Menu.Menu.Menu>}.
        """
        for player in self.CurrentMap.Players:
            if player.Win:
                self.TransitionToMenu('Retry Menu')
                self._menuDict['Retry Menu'].Background = pygame.display.get_surface().copy()
            
        
        if self.CurrentMap.WantsToSwitchMap:
            mapName, transfer = self.CurrentMap.MapSwitchParameters
            if mapName == Constants.GameConstants.NEXT_MAP:
                self.PlayNextMap(transfer)
            else:
                self.PlayMap(mapName, transfer)
                
    def BuildLevelSelection(self):
        """
        Builds the Level Select menu as well loading the level paths into the game.
        """
        levelSelectMenu = self.GetMenu('Level Select')
        levelCount = 0
        buttonPos = (100, 250)
        inc = 25
        fontPath = os.path.join(Constants.GameConstants.BASE_PATH, 'content/fonts/upheavtt.ttf')
        fontSize = 25
        fontColor = pygame.Color(220, 220, 220, 255)
        prevButton = levelSelectMenu.GetButton('Back')
        
        # load all maps
        mapDirectory = os.path.join(Constants.GameConstants.BASE_PATH, 'content/maps/')
        mapDirectory = os.path.realpath(os.path.normpath(mapDirectory))
        for root, dirs, files in os.walk(mapDirectory):
            for file in files:
                if file[-4:].lower() == '.tmx':
                    self.LoadMap(os.path.join(root, file))
                    # add a button to the level select menu
                    buttonName = 'Level ' + levelCount.__str__()
                    levelButton = PlatformerLevelSelectMenuButton(buttonName, file, buttonPos, fontPath, fontSize, file, fontColor, None)
                    levelSelectMenu.AddChild(levelButton)
                    
                    levelButton.AboveNeighborName = prevButton.Name
                    prevButton.BelowNeighborName = levelButton.Name
                    
                    levelCount += 1
                    buttonPos = (buttonPos[0], buttonPos[1] + inc)
                    prevButton = levelButton
            break
        
        levelSelectMenu.GetButton('Back').AboveNeighborName = prevButton.Name
        prevButton.BelowNeighborName = 'Back'
        
    def Run(self):
        """
        Loads Menus, Builds Level Selection, and goes to Main Menu before entering the Run loop.
        """
        self.LoadMenusFrom('config/menus/', self.Controllers)
        self.BuildLevelSelection()
        self.TransitionToMenu('Main Menu')
        
        Game.Run(self)