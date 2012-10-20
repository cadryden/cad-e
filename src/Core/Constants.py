'''
Consolidation of the constants used throughout the engine. 

Created on Mar 19, 2010

@author: Chris Alvarado-Dryden
'''
import pygame.locals
from Utilities.vector import Vector

class ActorConstants(object):
    MAX_X_VELOCITY = 5000.0
    MAX_Y_VELOCITY = 5000.0
    MAX_FALL_VELOCITY = 500.0
    
class CameraConstants(object):
    BORDER_WIDTH = 4.0
    BORDER_COLOR = pygame.Color(50, 50, 50)
    GRACE_TILES = 0
    
class ControllerConstants(object):
    CONTROLLERS_XML_PATH = '../config/controllers/controller.xml'
    DPAD_UP = 'DPad Up'
    DPAD_DOWN = 'DPad Down'
    DPAD_LEFT = 'DPad Left'
    DPAD_RIGHT = 'DPad Right'
    
    PAUSE_BUTTON = 'Pause'
    QUIT_BUTTON = 'Quit'
    
    JUMP_BUTTON = 'Jump'
    THROW_BUTTON = 'Throw'    
    
    

class EditorConstants(object):
    # property names to look for on the map
    MAP_PROP_GRAVITY = 'gravity'
    MAP_PROP_BACKGROUND = 'background'
    MAP_PROP_BACKGROUND_COLOR = 'background color'
    MAP_PROP_MUSIC = 'music'
    MAP_PROP_UI_FILES = 'ui files' 
    
    # layer names to look for
    LAYER_NAME_COLLISION_TILES = 'collision tiles'
    LAYER_NAME_COLLISION_GROUPS = 'collision groups'

    LAYER_NAME_CAMERAS = 'cameras'
    LAYER_NAME_CAMERA_COLLISION_TILES = 'camera collision'
    
    # layer properties to look for
    LAYER_PROP_ANIMATED = 'animated'
    
    # map object properties to look for
    OBJ_ACTOR_PROP_COLLISION_GROUPS = 'collision groups'
    OBJ_ACTOR_PROP_TRANSFER_NAME = 'transfer from'
    OBJ_CG_PROP_COLLIDES_WITH = 'collides with'
    OBJ_PLAYER_PROP_PLAYER_NUMBER = 'player'
    
    OBJ_CAM_PROP_TARGET = 'target'
    OBJ_CAM_PROP_DISP_VIEW = 'display view'
    OBJ_CAM_PROP_ORDER = 'order'
    OBJ_CAM_PROP_UI_FILE = 'ui files'
    
    # tile properties to look for
    TILE_PROP_TYPE = 'type'

class GameConstants(object):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    NEXT_MAP = 'next'

    MUSIC_VOLUME = 0.5
    SOUND_VOLUME = 0.5
    
    BASE_PATH = '..'    # just above src
    
class GameObjectConstants(object):
    DEBUG_COLOR = pygame.Color(255, 0, 0)
    
class MapConstants(object):
    DEFAULT_GRAVITY = (0, 1200)
    DEFAULT_CLEAR_COLOR = pygame.Color(64, 64, 64)
    
class MenuCosntants(object):
    BUTTON_ABOVE = 'above'
    BUTTON_BELOW = 'below'
    BUTTON_LEFT = 'left'
    BUTTON_RIGHT = 'right'
    
    PAUSE_MENU_NAME = 'Pause Menu'
    
class PlayerConstants(object):
    PLAYER_1_BUTTONS = [[ControllerConstants.JUMP_BUTTON, pygame.locals.K_SPACE, pygame.locals.K_w], [ControllerConstants.THROW_BUTTON, pygame.locals.K_SPACE]]
    PLAYER_1_DPAD = [pygame.locals.K_w, pygame.locals.K_s, pygame.locals.K_a, pygame.locals.K_d]
    
    MAX_X_VELOCITY = 400000.0
    MAX_Y_VELOCITY = 3000.0
    MAX_FALL_VELOCITY = 375.0
    
    MAX_RUN_VELOCITY = 300.0
    MAX_JUMP_VELOCITY = 600.0
    
    DEFAULT_THROW_VECTOR = Vector((800, -400))
    THROW_COOLDOWN = 1.25

class StateConstants(object):
    # move to examples? CAD
    IDLE_NAME = 'idle'
    RUN_NAME = 'run'
    JUMP_NAME = 'jump'
    FALL_NAME = 'fall'
    LAND_NAME = 'land'
    THROW_NAME = 'throw'
    
    # Camera states
    CAM_TRACK_TARGET_NAME = 'targetting'
    CAM_STATIC_NAME = 'static'

class TileConstants(object):
    SIDE_TOP = 'top'
    SIDE_BOTTOM = 'bottom'
    SIDE_LEFT = 'left'
    SIDE_RIGHT = 'right'
