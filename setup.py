from distutils.core import setup

setup(name='Busic', # the package/module name
      version='1.0', # the version (an arbitrary string)
      author='Bolong Zeng', 
      author_email='bzeng@wsu.edu', 
      py_modules=[ 'Busic', 'hoverable', 'player', 'synclyrics' ],
      data_files = [('lib/site-packages/Busic', ['busic.kv']), 
                    ('lib/site-packages/Busic/img', ['img/delete.png', 'img/help.png', 'img/ico.txt', 'img/importdoc.png',                        'img/inserttime.png',
                              'img/music.png', 'img/mute.png', 'img/notepad.png', 'img/pause.png', 'img/play.png', 'img/save.png',
                               'img/saveas.png', 'img/stop.png', 'img/volume.png']),
                     ('lib/site-packages/Busic/music', ['music/Anything_Goes.ogg', 
                                'music/I_See_Fire.ogg', 'music/I_See_Fire.txt', 'music/I_See_Fire.lrc',
                                'music/Ladies_Who_Lunch.ogg',
                                'music/Ladies_Who_Lunch.lrc',
                                'music/Ladies_Who_Lunch.txt']) 
                    ],
      platforms = ('Windows 7')
      )