'''
A single sound clip, loaded from file.

Created on May 28, 2010

@author: Chris Alvarado-Dryden
'''
import pygame
import random
import os

class Sound(object):
    """
    A single sound clip, loaded from file.  Each sound is controlled like it's own self contained audio player, and has
    play/pause/stop functionality.  The Sound class wraps the C{U{pygame.mixer<http://www.pygame.org/docs/ref/mixer.html>}},
    C{U{pygame.mixer.Sound<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound>}}, and
    C{U{pygame.mixer.Channel<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel>}} classes, which means the
    same file types are supported (.OGG, .WAV).  Unlike in pygame, however, multiple Sound objects can reference the
    same file, and all have different volumes and be played on top of each other.  Effectively, they are completely
    different sounds.
    
    To use sounds there are some requirements/suggestions:
        - Use .OGG or uncompressed .WAV audio files.
        - All sounds used should have the same frequency, and bit size per sample.
        - Only a certain number of sounds can be played simultaneously.  See the C{channels} argument of
        L{Sound.Initialize}.
    
    While the Sound class could be used for music, be aware that any Sound can preempt another in order to play
    itself.  To avoid this for music, consider the L{MusicPlayer<MusicPlayer.MusicPlayer>}.
    
    @type Initialized:         C{bool}
    @cvar Initialized:         C{True} if L{Sound.Initialize} has been called, C{False} otherwise.  This should be treated
                               as read only.
    
    @type loadedSounds:        C{dict}
    @cvar loadedSounds:        C{{str : U{pygame.mixer.Sound<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound>}}} -
                               A dictionary of sound file paths and their 
                               C{U{pygame.mixer.Sound<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound>}} objects.
                               This is used to prevent reloading the same audio files multiple times.  It is populated as
                               the files are loaded.
    
    @type _initParams:         C{list}
    @cvar _initParams:         Initialization parameters, stored to reinitialize the sound system. 

    @type _path:               C{str}
    @ivar _path:               Absolute file path to the sound file.
    
    @type _pySound:            C{U{pygame.mixer.Sound<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound>}}
    @ivar _pySound:            The pygame sound object this Sound represents.
    
    @type _volume:             C{float}
    @ivar _volume:             Volume for this sound, in range [0.0, 1.0].
    
    @type _channel:            C{U{pygame.mixer.Channel<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel>}}
    @ivar _channel:            The channel that this is playing on.
    
    @type _loops:              C{int}
    @ivar _loops:              The number of times the sound should loop.
    
    @type _playing:            C{bool}
    @ivar _playing:            C{True} if the sound is being played, C{False} otherwise.  Mutually exclusive with Paused
                               and Stopped.
    
    @type _paused:             C{bool}
    @ivar _paused:             C{True} if the sound is paused, C{False} otherwise.  Mutually exclusive with Playing
                               and Stopped.
    
    @type _stopped:            C{bool}
    @ivar _stopped:            C{True} if the sound is stopped, C{False} otherwise.  Mutually exclusive with Playing and
                               Paused.
    """
    
    _initParams = ()
    loadedSounds = {}
    Initialized = False

    @staticmethod
    def Initialize(rate=44100, bits=16, stereo=False, channels=8):
        """
        Initializes the sound system.
        
        @type  rate:        C{int}
        @param rate:        Sample rate for all sounds, in hertz.
        
        @type  bits:        C{int}
        @param bits:        Bits used per sample. 
        
        @type  stereo:      C{bool}
        @param stereo:      C{True} if stereo, C{False} if mono.
        
        @type  channels:    C{int}
        @param channels:    The number of channels available to play sound on simultaneously.
        """
        if stereo:
            stereoInt = 2
        else:
            stereoInt = 1

        buffer = int(2048 * (rate / 44100.0))

        Sound._initParams = ([rate, -bits, stereoInt, buffer], channels)
        Sound.Reinitialize()
        Sound.Initialized = True

    @staticmethod
    def Reinitialize():
        """
        Reinitializes the sound system using the same parameters as the first initialization.
        """
        rate, bits, stereoInt, buffer = Sound._initParams[0]
        channels = Sound._initParams[1]

        pygame.mixer.quit()
        pygame.mixer.init(rate, bits, stereoInt, buffer)
        pygame.mixer.set_num_channels(channels)

    @staticmethod
    def __get_free_channel__():
        """
        Returns a Channel which is not currently playing a sound.  If none are available, returns channel 0.
        
        @rtype:        C{U{pygame.mixer.Channel<http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel>}}
        @return:       A free channel, or channel 0 if all are actively playing.
        """
        channelIDs = range(pygame.mixer.get_num_channels())
        random.shuffle(channelIDs)

        for i in channelIDs:
            chan = pygame.mixer.Channel(i)
            if not chan.get_sound():
                return chan

        return pygame.mixer.Channel(0)

    def __init__(self, path, volume, loops=0):
        """
        Creates a new Sound by loading the file at the given path.  It will be played with the given volume, and
        will loop the given amount of times.  Zero loops means it will only play once.
        
        @type  path:            C{str}
        @param path:            Absolute file path to the audio file.
        
        @type  volume:          C{float}
        @param volume:          Volume in range [0.0, 1.0].
        
        @type  loops:           C{int}
        @param loops:           The number of times this sound should loop.  Defaults to 0 loops, which means it
                                will only play once.
        """
        # get the sound
        self._path = os.path.abspath(path)
        if os.path.isfile(self._path):
            if (Sound.loadedSounds.has_key(self._path)):
                self._pySound = Sound.loadedSounds[self._path]
            else:
                self._pySound = pygame.mixer.Sound(self._path)
                Sound.loadedSounds[self._path] = self._pySound
        else:
            raise Exception('File could not be found: "' + self._path + '"')
        
        self._channel = None
        
        self._loops = loops
        
        # set _volume
        self.Volume = volume
        
        # set the statuses
        self._playing = False
        self._paused = False
        self._stopped = True
    
    def Copy(self):
        """
        Creates a copy this Sound.
        
        @rtype:        C{Sound}
        @return:       A copy of this Sound.
        """
        return Sound(self._path, self._volume, self._loops)
    
    def Play(self):
        """
        Plays the sound.  If paused, resumes it, if already playing does nothing.
        """
        # do not restart if we are already playing
        if self.Playing:
            return
        
        if self._channel:
            self._channel.unpause()
        else:
            self._channel = Sound.__get_free_channel__()
            self.__set_volume__(self._volume)
            self._channel.play(self._pySound, self._loops)
            
        self._playing = True
        self._stopped = False
        self._paused = False

    def Pause(self):
        """
        Pauses the sound.  To resume, use L{Play()<Sound.Sound.Play>}. 
        """
        if self.Stopped:
            return
        
        if self._channel:
            self._channel.pause()
            
        self._paused = True
        self._playing = False
        self._stopped = False    

    def Stop(self):
        """
        Stops the sound, and resets it to play from the beginning.  Also frees a channel to be used by another Sound.
        """
        if self._channel:
            self._channel.stop()
            self._channel = None
            
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
        if self._channel:
            self._channel.set_volume(self._volume)
            
    def __is_playing__(self):
        return self._playing and self._channel and (self._channel.get_sound() is self._pySound)
    def __is_paused__(self):
        return self._paused
    def __is_stopped__(self):
        return not self._channel or (self._channel.get_sound() is not self._pySound)
            
    Volume = property(__get_volume__, __set_volume__, None, "Volume of this sound, between 0.0 and 1.0.")
    Playing = property(__is_playing__, None, None, "C{True} if the sound is playing, C{False} otherwise.")
    Paused = property(__is_paused__, None, None, "C{True} if the sound is paused, C{False} otherwise.")
    Stopped = property(__is_stopped__, None, None, "C{True} if the sound is stopped, C{False} otherwise.")