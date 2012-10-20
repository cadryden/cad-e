'''
An audio player used to stream music from a file.

@author: Chris Alvarado-Dryden
'''
import os
import pygame
from Core.Sound import Sound

class MusicPlayer(object):
    """
    An audio player used to stream music from a file.  The music player has standard play/pause/stop functionality
    and can only have a single file loaded and being played at a time.  The player works best with .OGG files,
    but there is limited support for .MP3 as well.
    
    This class follows the singleton design pattern.  The first call to the constructor will create a new instance,
    but all subsequent calls will return the original instance.  It wraps
    U{pygame.mixer.music<http://www.pygame.org/docs/ref/music.html>}.
    
    @type _instance:           C{MusicPlayer}
    @cvar _instance:           The single instance of the MusicPalyer class.
    
    @type _initialized:        C{bool}
    @cvar _initialized:        C{True} if the single instance of the MusicPlayer has been initialized, C{False} otherwise.
    
    @type _volume:             C{float}
    @ivar _volume:             Volume for this music player, in range [0.0, 1.0].
    
    @type _playing:            C{bool}
    @ivar _playing:            C{True} if the music is being played, C{False} otherwise.  Mutually exclusive with Paused
                               and Stopped.
    
    @type _paused:             C{bool}
    @ivar _paused:             C{True} if the music is paused, C{False} otherwise.  Mutually exclusive with Playing
                               and Stopped.
    
    @type _stopped:            C{bool}
    @ivar _stopped:            C{True} if the music is stopped, C{False} otherwise.  Mutually exclusive with Playing and
                               Paused.
    """
    _instance = None
    _initialized = False

    def __new__(self):
        """
        If no MusicPlayer has been created, instantiates a new one, otherwise returns the single instance.
        
        @rtype:        C{MusicPlayer}
        @return:       The single instance of MusicPlayer.
        """
        if not MusicPlayer._instance:
            # magic?
            MusicPlayer._instance = super(MusicPlayer, self).__new__(self)
        
        return MusicPlayer._instance
        
        
    def __init__(self):
        """
        Initializes instance variables for the MusicPlayer if it hasn't already been initialized.
        """
        if MusicPlayer._initialized:
            return

        self._volume = 1.0
        
        # set the statuses
        self._playing = False
        self._paused = False
        self._stopped = True
        
        MusicPlayer._initialized = True
        
    def Load(self, path):
        """
        Loads the audio file at the given path and prepares it for playing.  If music is already being played, it will
        be stopped.
        
        @type  path:        C{str}
        @param path:        Path to the audio file to load.
        """
        if Sound.Initialized:
            self.Stop()
            pygame.mixer.music.load(os.path.abspath(path))
        else:
            raise Exception('Sound system has not been initialized.  Sound.Initialize() must be called before loading music.')
        
    def Play(self, loops=-1):
        """
        Plays the loaded music on this MusicPlayer.  If paused, it will be resumed, if already playing it will do nothing.
        The C{loops} parameter is only used if the music L{stopped<MusicPlayer.MusicPlayer.Stop>} prior to this call.
        
        @type  loops:        C{int}
        @param loops:        Number of times the audio should loop.  If -1, will loop indefinitely.  If 0, the music
                             will not loop, and only play once.
        """
        
        # do not restart if we are already playing
        if self.Playing:
            return
        
        if self.Paused:
            pygame.mixer.music.unpause()
        else:
            if loops >= 0:
                # pygame documentation wrong
                loops += 1
            pygame.mixer.music.play(loops)
        
        self._playing = True
        self._stopped = False
        self._paused = False
        
    def Pause(self):
        """
        Pauses the music.  To resume play, use L{MusicPlayer.Play()<MusicPlayer.MusicPlayer.Play>}.
        """
        if self.Stopped:
            return
        
        pygame.mixer.music.pause()
        
        self._paused = True
        self._playing = False
        self._stopped = False    
        
    def Stop(self):
        """
        Stops the music, and resets it to play from the beginning.
        """
        pygame.mixer.music.stop()
        pygame.mixer.music.rewind()
        
        self._stopped = True
        self._playing = False
        self._paused = False
    
    ############### PROPERTIES ###############
    
    def __get_volume__(self):
        return self._volume
    def __set_volume__(self, value):
        if value < 0.0:
            self._volume = 0.0
        elif value > 1.0:
            self._volume = 1.0
        else:
            self._volume = value
        
        pygame.mixer.music.set_volume(self._volume)
        
    def __is_playing__(self):
        return self._playing
    def __is_paused__(self):
        return self._paused
    def __is_stopped__(self):
        return self._stopped
            
    Volume = property(__get_volume__, __set_volume__, None, "Volume of this music player, between 0.0 and 1.0.")
    Playing = property(__is_playing__, None, None, "C{True} if music is playing, C{False} otherwise.")
    Paused = property(__is_paused__, None, None, "C{True} if music is paused, C{False} otherwise.")
    Stopped = property(__is_stopped__, None, None, "C{True} if music is stopped, C{False} otherwise.")