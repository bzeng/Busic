import kivy
kivy.require('1.8.0') # replace with your current kivy version !
from kivy.core.audio import SoundLoader
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.factory import Factory
from kivy.uix.widget import Widget
from pygame import mixer
from pygame.mixer import music

import re

class Player(Widget):
    file = StringProperty(None)
    sound = ObjectProperty(None)
    length = NumericProperty(None)
    
    prevvolume = NumericProperty(0.0)
    #pausetime = NumericProperty(None)
    
    def load(self):
        try:
            mixer.init(44100, -16, 1, 4096)
            self.sound = SoundLoader.load(self.file)
            self.length = self.sound.length
            #print('length: ' + str(self.length))
            music.load(self.file)
            if not self.sound:
                self.parent.statuschange('Unsupported music file: ' + self.file)
            else:
                #print('Music loaded: ' + self.file)                
                self.sound.unload()
        except Exception as e:
            print(e)
            
    def unload(self):
        self.file = ''
        self.length = 0
    
    def play(self, start=0.0):
        try:
            if not music.get_busy():                
                music.play()
            elif start == 0.0:
                music.unpause()                    
            else:
                print(start)
                music.play(start=start)
        except Exception as e:
            print(e)
            print('Unsupported music file')
            
    def pause(self):
        music.pause()
        
    def stop(self):        
        # if self.sound:
            # self.pausetime = 0
            # self.sound.stop()
            # self.sound.seek(0)
            # print("Sound stop with %s" % self.sound.source)
        music.stop()  
        
    def get_busy(self):
        return music.get_busy()

    def get_pos(self):
        return music.get_pos()
        
    def mute(self):
        self.prevvolume = music.get_volume()
        music.set_volume(0.0)
        
    def unmute(self):
        if self.prevvolume != 0:
            music.set_volume(self.prevvolume)
        
    #def set_pos(self, pos):
    #    music.set_pos(pos)

    