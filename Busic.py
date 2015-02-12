import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.listview import ListView, ListItemButton, ListItemLabel
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup


from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty, DictProperty

 
from kivy.effects.scroll import ScrollEffect
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.garden.filebrowser import FileBrowser

from hoverable import HoverBehavior
from player import Player
from synclyrics import SyncLyrics
from os.path import sep, expanduser, isdir, dirname

import sys
import os
import math
import json

        
class MyListItemButton(ListItemButton):
    filename = StringProperty(None)

class ScrollableLabel(ScrollView):
    
    text = StringProperty('')
    color = ListProperty(None)

class LoadFileBrowser(FileBrowser):
    def __init__(self, **kwargs):
        if sys.platform == 'win32':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
            
        super(LoadFileBrowser, self).__init__(favorites=[(user_path, 'Documents')], **kwargs)

class ToolBar(Widget):    
    #loadfile = ObjectProperty(None)
    #savefile = ObjectProperty(None)
    player = ObjectProperty(None)
    lyricsfilename = StringProperty(None)
    text_input = ObjectProperty(None)    
    
    def dismiss_popup(self, instance):
        self._popup.dismiss()

    def loadmusic(self):
        #content = LoadDialog(load=self.load, cancel=self.dismiss_popup, filters=['*.wav', '*.ogg'])
        content = LoadFileBrowser(select_string='Select Music', filters=['*.ogg'], path=os.getcwd())
        content.bind(on_success=self.load, on_canceled=self.dismiss_popup)
        self._popup = Popup(title="Load music", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        
    def savelyrics(self):
        if self.lyricsfilename is not None:
            try:
                with open(self.lyricsfilename, 'w') as stream:
                    stream.write(self.parent.parent.lyricstext.text)
                #self.lyricsfilename = filename
                self.statuschange('Lyrics saved to ' + self.lyricsfilename)
            except Exception as e:
                print(e)
                self.statuschange('Saving lyrics failed! Unexpected exception.')
        else:
            self.savelyricsas()
            
    def loadlyrics(self):
        content = LoadFileBrowser(select_string='Select Lyrics', filters=['*.lrc', '*.txt'], path=os.getcwd())
        content.bind(on_success=self.loadlrc, on_canceled=self.dismiss_popup)
        self._popup = Popup(title="Load lyrics", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        
    def savelyricsas(self):
        content = LoadFileBrowser(select_string='Save Lyrics', filters=['*.lrc', '*.txt'], path=os.getcwd())
        content.bind(on_success=self.save, on_canceled=self.dismiss_popup)
        self._popup = Popup(title="Save lyrics", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        
    def loadlrc(self, instance):
        filename = instance.selection
        self.lyricsfilename = filename[0]
        self.parent.parent.loadlrc(self.lyricsfilename)    
        self.dismiss_popup(instance)        
        
    def save(self, instance):
        
        spath = instance.path.replace('/', os.sep)
        sname = instance.filename.replace('/', os.sep)
        if spath in sname:
            textinput = instance.filename
        else:
            textinput = instance.path + os.sep + instance.filename
        if instance.selection != []:
            if textinput != instance.selection[0] and textinput != '':
                filename = textinput
            else:
                filename = instance.selection[0]
        else:
            filename = textinput
        if filename is not '' and not filename.endswith('.txt') and not filename.endswith('.lrc'):
            filename += '.txt'
        try:            
            with open(filename, 'w') as stream:
                stream.write(self.parent.parent.lyricstext.text)
            
            self.lyricsfilename = filename
            self.parent.parent.setlrcfilename(self.lyricsfilename)
            #self.statuschange('Lyrics saved to ' + filename[filename.rindex(os.sep)+1:])
        except Exception as e:
            print(e)
            self.statuschange('Saving lyrics failed! Unexpected exception.')
            
        self.dismiss_popup(instance)
    
    '''
    Playback controls
    '''
    def load(self, instance, file=''):
        try:
            if self.player.get_busy():
                self.stop()
            if file == '':
                filename = instance.selection
                #print(filename)        
                audiofile = filename[0]
                self.dismiss_popup(instance)
            else:
                audiofile = file
            #print(audiofile)
            self.player.file = audiofile
            self.player.load()
            self.parent.parent.loadsong(audiofile, self.player.length)
            self.statuschange(audiofile[audiofile.rindex(os.sep)+1:] + ' loaded!')
        except Exception as e:
            print(e)
            self.statuschange('Loading music failed. Unexpected error.')
    
    def unload(self):
        self.player.unload()
            
    def play(self):
        if self.player.length != 0:
            self.player.play()
            self.parent.parent.playsong()
        else:
            self.statuschange('No music loaded yet.')
        
    def pause(self):
        if self.player.length != 0:
            self.player.pause()        
            self.parent.parent.pausesong()
        else:
            self.statuschange('No music loaded yet.')
    
    def stop(self):
        if self.player.length != 0:
            self.player.stop()
            self.parent.parent.stopsong()
        else:
            self.statuschange('No music loaded yet.')
        
    '''
    Insert time stamps.
    '''    
    def get_time(self):
        current_timestamp = self.player.get_pos()
        return current_timestamp
        
    def inserttime(self):
        self.parent.parent.lyricstext.insert_timestamp()
        
        
    '''
    Music list (if lib.json exists) will be automatically loaded. 
    Save music list.
    Delete music from list.
    '''
    def savelist(self):
        self.parent.parent.savejson()        
        
    def deletelist(self):
        self.parent.parent.listdelete()
    
    def help(self):
        helptext = """        
        1. Load music: load a song from the file system. Only supports .ogg now. \n
           The music is added to the playlist. \n
        2. Play/Pause/Stop: basic playback control. \n
        3. Load lyrics: load a lyrics file into the input entry. Supports either \n
           .txt or .lrc file. \n
        4. Save (F6)/Save as (F12): save the lyrics file to the file system. \n
        5. Insert timestamp (F5): insert the current timestamp when the muisc \n
           is playing at the beginning of the current line. \n
        6. Save playlist: save the playlist to file lib.json. \n
        7. Delete from playlist: remove selected songs from the playlist. \n
        8. Help: display this help message.
        """
        popup = Popup(title='Help', content=Label(text=helptext),  size_hint=(.8, .8))
        popup.open()
    
    def statuschange(self, text=''):
        self.parent.parent.statuschange(text)
        
class LyricsInput(TextInput):
    # def __init__(self, **kwargs):
       # super(LyricsInput, self).__init__(**kwargs)
       # self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
       # self._keyboard.bind(on_key_down=self._keyboard_on_key_down)
       
    # def _keyboard_closed(self):
        # self._keyboard.unbind(on_key_down=self._keyboard_on_key_down)
        # self._keyboard = None      
    lyricsfilename = StringProperty(None)
    lines = NumericProperty(0)
      
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        #print(keycode[1])  
        if keycode[1] == 'f5':
            self.insert_timestamp()
        elif keycode[1] == 'f6':
            self.savelyrics()
        elif keycode[1] == 'f7':
            self.loadlyrics()
        elif keycode[1] == 'f12':
            self.savelyricsas()
        
        return super(LyricsInput, self)._keyboard_on_key_down(window, keycode, text, modifiers)

    def insert_timestamp(self):
        self.cursor = (0, self.cursor_row)
        time = self.parent.parent.parent.parent.parent.parent.gettimestamp()
        if time is not None:
            timestamp = '[' + time + ']'
            self.insert_text(timestamp)
            self.cursor = (0, self.cursor_row+1)
            if self.lines != 0:
                if self.parent.scroll_y > 0:
                    self.parent.scroll_y -= 1 / self.lines
                else:
                    self.parent.scroll_y = 0

    def insert_text(self, substring, from_undo=False):        
        s = substring.replace('\r','')
        self.count_lines(s)
        return super(LyricsInput, self).insert_text(s, from_undo=from_undo)
        
    def count_lines(self, s):
        for c in s:
            if c == '\n':
                self.lines += 1
        
    def savelyrics(self):
        if self.lyricsfilename is not None:
            try:
                with open(self.lyricsfilename, 'w') as stream:
                    stream.write(self.text)
                filename = self.lyricsfilename
                self.statuschange('Lyrics saved to ' + filename[filename.rindex(os.sep)+1:])
            except Exception as e:
                print(e)
                self.statuschange('Saving lyrics failed! Unexpected exception.')
        else:
            self.savelyricsas()
            
    def savelyricsas(self):
        content = LoadFileBrowser(select_string='Save Lyrics', filters=['*.lrc', '*.txt'], path=os.getcwd())
        content.bind(on_success=self.save, on_canceled=self.dismiss_popup)
        self._popup = Popup(title="Save lyrics", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        
    def save(self, instance):
        spath = instance.path.replace('/', os.sep)
        sname = instance.filename.replace('/', os.sep)
        if spath in sname:
            textinput = instance.filename
        else:
            textinput = instance.path + os.sep + instance.filename
        if instance.selection != []:
            if textinput != instance.selection[0] and textinput != '':
                filename = textinput
            else:
                filename = instance.selection[0]
        else:
            filename = textinput
        #print(filename)
        if filename is not '' and not filename.endswith('.txt') and not filename.endswith('.lrc'):
            filename += '.txt'
        try:
            with open(filename, 'w') as stream:
                stream.write(self.text)
            self.lyricsfilename = filename  
            self.parent.parent.parent.parent.parent.parent.setlrcfilename(filename)
            #self.statuschange('Lyrics saved to ' + filename[filename.rindex(os.sep)+1:])
        except Exception as e:
            print(e)
            self.statuschange('Saving lyrics failed! Unexpected exception.')
            
        self.dismiss_popup(instance)
     
    def loadlyrics(self):
        content = LoadFileBrowser(select_string='Select Lyrics', filters=['*.lrc', '*.txt'], path=os.getcwd())
        content.bind(on_success=self.loadlrc, on_canceled=self.dismiss_popup)
        self._popup = Popup(title="Load lyrics", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
        
    def loadlrc(self, instance):
        filename = instance.selection
        self.lyricsfilename = filename[0]
        self.parent.parent.parent.parent.parent.parent.loadlrc(self.lyricsfilename)    
        self.dismiss_popup(instance) 
     
    def dismiss_popup(self, instance):
        self._popup.dismiss()
        
    def statuschange(self, text=''):
        self.parent.parent.parent.parent.parent.parent.statuschange(text)

class MainUI(Widget):
    songlength = StringProperty(None)
    toolbar = ObjectProperty(None)
    timelabel = ObjectProperty(None)
    sliderbar = ObjectProperty(None)
    lyricstext = ObjectProperty(None)
    
    lyricsfilename = StringProperty(None)
    
    synclyrics = ObjectProperty(None)
    localtimes = ListProperty(None)
    localtimesindex = NumericProperty(0)
    
    lrclines = NumericProperty(None)
    active_color_head = StringProperty('[color=#00FF00]')
    nonactive_color_head = StringProperty('[color=#008000]')
    color_tail = StringProperty('[/color]')
    
    musiclist = ObjectProperty(None)
    musiclistadapter = ObjectProperty(None)
    musicdata = DictProperty(None)
    musiclistdata = ListProperty(None)
    
    statusbar = ObjectProperty(None)
    volumebutton = ObjectProperty(None)
    
    def sec_to_string(self, length):
        if length == 0:
            length = 0.0
        min = int(length // 60)
        sec = int(length - min * 60)
        milsec = str(length - math.floor(length))
        milsec = milsec.split('.')[1]
        totallength = '{:02d}:{:02d}.{:.2s}'.format(min, sec, milsec)
        return totallength
    
    def loadsong(self, file, length):
        #length here return by kivy is in seconds.
        
        self.songlabel.text = file[file.rindex(os.sep)+1:]
        self.songlength = self.sec_to_string(length)
        self.timelabel.text = '{} / {}'.format('00:00.00', self.songlength)
        self.togglevolume(self.volumebutton, mute=False)
        self.setslider(length)                
        self.sliderbar.bind(value=self.slider_value_change)
        if self.localtimes is not None:
            self.localtimes.append(length)
            self.localtimes.append(0)       
         
        if file not in self.musicdata:
            self.musicdata[file] = {'name': self.songlabel.text}#, 'length': length}
            tmp_text = "{}".format(self.musicdata[file]['name'])#, self.musicdata[file]['length'])
            tmp_data = {'text': tmp_text, 'is_selected': False, 'filename': file}
            self.musiclistdata.append(tmp_data)
            self.populate_listview()
        else:
            pass
            
        #self.sliderbar.bind(on_touch_down=self.slider_click)
        
    def playsong(self):
        #pos here return by player is in milseconds
        Clock.schedule_interval(self.clockcall, 0.01)
        
    def pausesong(self):
        Clock.unschedule(self.clockcall)    
    
    def stopsong(self):
        Clock.unschedule(self.clockcall)        
        self.sliderbar.value = 0
        self.previewlabel.scroll_y = 1
        self.localtimesindex = 0
        
    def clockcall(self, dt):
        self.sliderbar.value = self.toolbar.player.get_pos() // 10 / 100
        
    def setslider(self, length):
        self.sliderbar.max = length
        
    def slider_value_change(self, instance, value):
        if value < 0:
            self.sliderbar.value = 0
            Clock.unschedule(self.clockcall)
        current_pos = self.sec_to_string(value)
        self.timelabel.text = '{} / {}'.format(current_pos, self.songlength)
        
        #scroll the preview here
        if self.lyricsfilename is not None and self.lyricsfilename.endswith('.lrc'):
            val1 = self.localtimes[self.localtimesindex]
            val2 = self.localtimes[self.localtimesindex+1]
            if value >= val1 and value <= val2:
            #if value in self.localtimes:
                self.localtimesindex += 1
                #print(str(val1) + '<=' + str(value) + '<=' + str(val2))
                #tmp_value = value
                
                self.scroll_preview(val1)
            
    def scroll_preview(self, value):
        #Active [color=#00FF00]Hello[/color]
        #Nonactive [color=#008000]Hello[/color]        
        str_lrc = ''
        for key in sorted(self.synclyrics.syncdict):
            tmp_line = self.synclyrics.syncdict[key]
            if key == value:
                cur_line = tmp_line.replace(self.nonactive_color_head, self.active_color_head)
                str_lrc += cur_line + '\n'
            else:
                str_lrc += tmp_line + '\n'
        self.previewlabel.text = str_lrc
        if self.previewlabel.scroll_y == 1:
            self.previewlabel.scroll_y -= 0.0001 / self.lrclines
        elif self.previewlabel.scroll_y > 0:
            self.previewlabel.scroll_y -= 1 / self.lrclines
        else:
            self.previewlabel.scroll_y = 0
        
    #seeking is not working    
    def slider_click(self, instance, value):
        try:
            print(instance.size)
            print('try seeking')
            new_pos = self.sliderbar.value
            print(new_pos)
            #self.toolbar.player.play(start=new_pos)
        except Exception as e:
            print(e)
            print('Seek position not supported for this codec')
            
    '''
    For inserting time stamp, and lyrics related loading and saving
    '''
    def gettimestamp(self):
        if self.songlength is not None:
            return self.sec_to_string(self.toolbar.get_time() / 1000)
        else:
            return None
            
    def loadlrc(self, filename):
        try:
            with open(filename, 'r') as stream:
                self.lyricstext.lines = 0
                self.lyricstext.text = ''
                self.lyricstext.insert_text(stream.read())
                if filename.endswith('.txt'):
                    self.previewlabel.text = self.lyricstext.text
                    self.statuschange('Regular lyrics loaded.')
                else:
                    #parse the lrc file
                    self.synclyrics = SyncLyrics(self.lyricstext.text)                    
                    self.previewlabel.text = self.synclyrics.strippedlrc
                    self.lrclines = len(self.synclyrics.syncdict)
                    self.localtimes = sorted(list(self.synclyrics.syncdict.keys()))
                    if self.sliderbar.max != 0:
                        self.localtimes.append(self.sliderbar.max)
                        self.localtimes.append(0)
                    #print(self.localtimes)
                    self.statuschange('Synced lyrics loaded.')
            self.lyricsfilename = filename
            self.lyriclabel.text = filename[filename.rindex(os.sep) + 1:]
            
        except Exception as e:
            print(e)
            self.statuschange('Loading lyrics failed!')
        
    def setlrcfilename(self, filename):
        try:
            if filename.endswith('.txt'):
                self.previewlabel.text = self.lyricstext.text
            else:
                #parse the lrc file
                self.synclyrics = SyncLyrics(self.lyricstext.text)                    
                self.previewlabel.text = self.synclyrics.strippedlrc
                self.lrclines = len(self.synclyrics.syncdict)
                self.localtimes = sorted(list(self.synclyrics.syncdict.keys()))
                if self.sliderbar.max != 0:
                    self.localtimes.append(self.sliderbar.max)
                    self.localtimes.append(0)
        
            self.lyricsfilename = filename
            self.lyriclabel.text = filename[filename.rindex(os.sep) + 1:]
            self.lyricstext.lyricsfilename = filename
            self.statuschange('Lyrics saved to ' + self.lyriclabel.text)
        except Exception as e:
            print(e)
            self.statuschange('Unexpected error while saving lyrics.')
            
    def loadjson(self, lib='lib.json'):
        libpath = os.getcwd() + os.sep + lib
        #print(libpath)
        try:
            if os.path.isfile(libpath): 
                with open(libpath, 'r') as stream:    
                    self.musicdata = json.loads(stream.read())
                #[{'text': str(i), 'is_selected': False} for i in range(100)]
                #if self.musicdata is not {:
                #print(self.musicdata)
                for k in self.musicdata:
                    if os.path.isfile(k): 
                        tmp_text = "{}".format(self.musicdata[k]['name'])#, self.sec_to_string(self.musicdata[k]['length']))
                        tmp_data = {'text': tmp_text, 'is_selected': False, 'filename': k}
                        self.musiclistdata.append(tmp_data)
                    else:
                        del self.musicdata[k]
                self.populate_listview()
                self.statuschange('Library loaded from ' + libpath + '.')
        except Exception as e:
            print(e)
            self.statuschange('Loading library at ' +libpath+ ' failed.') 
        
    def populate_listview(self):
        args_converter = lambda row_index, rec: {'text': rec['text'],
                                                 'size_hint_y': None,
                                                 'height': 25,
                                                 'filename': rec['filename']}
        #print(self.musiclistdata)
        self.musiclistadapter = ListAdapter(data=self.musiclistdata,
                                   args_converter=args_converter,
                                   cls=MyListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=True)
        self.musiclist.adapter = self.musiclistadapter        
        self.musiclist.adapter.bind(on_selection_change=self.listselect) 
        self.musiclist.populate()
        #return None
    
    def listselect(self, instance):
        if self.musiclist.adapter.selection:
            filename = instance.selection[0].filename
            self.toolbar.load(None, file=filename)
        
    def listdelete(self):
        if self.musiclist.adapter.selection:
            delname = self.musiclist.adapter.selection[0].filename
            del self.musicdata[delname]
            #print(delname)        
            for i in self.musiclist.adapter.data:
                if i['filename'] == delname:
                    self.musiclist.adapter.data.remove(i)                    
                    break
            self.musiclist.populate()
            
            if delname == self.toolbar.player.file:
                self.toolbar.stop()
                self.songlength = '00:00.00'
                self.timelabel.text = '{} / {}'.format('00:00.00', self.songlength)
                self.songlabel.text = 'Music not selected yet.'
                self.localtimes = []            
                self.toolbar.unload()
            self.statuschange(delname[delname.rindex(os.sep) + 1:] + ' deleted.')        
        else:
            self.statuschange('No selection to be deleted.')                    
        
    def savejson(self, lib='lib.json'):
        libpath = os.getcwd() + os.sep + lib
        #print(libpath)
        self.statuschange('Saving library to ' + libpath + '...')
        try:
            if self.musicdata is not None:                 
                with open(libpath, 'w') as stream:  
                    stream.write(json.dumps(self.musicdata))
                self.statuschange('Library saved to ' + libpath + '.')
        except Exception as e:
            print(e)
            #print('Saving json file failed')
            self.statuschange('Saving json file failed.')
            
    def statuschange(self, text=''):
        self.statusbar.title = text
        pass
        
    def togglevolume(self, instance, mute=True):
        #s = Slider(min=0.0, max=1.0, value=0.5, orientation='vertical', pos=instance.pos)
        if instance.icon == 'img/volume.png' and mute:
            instance.icon = 'img/mute.png'
            self.toolbar.player.mute()
        else:
            instance.icon = 'img/volume.png'
            self.toolbar.player.unmute()


class BusicApp(App):

    def build(self):
        mainUI = MainUI()        
        mainUI.loadjson()
        return mainUI

if __name__ == '__main__':
    BusicApp().run()