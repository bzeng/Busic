"""Hoverable Behaviour (changing when the mouse is on the widget by O. Poyen.
License: LGPL
"""
__author__ = 'Olivier POYEN'

from kivy.uix.bubble import Bubble
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.factory import Factory

class TipBubble(Bubble):
    text = StringProperty(None)

class HoverBehavior(object):
    """Hover behavior.

    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget 
    """

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    hovertext = StringProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)


    def on_mouse_pos(self, *args):
        pos = args[1]
        inside = self.collide_point(*pos)
        if self.hovered == inside:
            #We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        if not hasattr(self, 'bubb'):
            self.bubb = bubb = TipBubble(text=self.hovertext, pos=self.pos)
            self.add_widget(bubb)
        else:
            values = ('left_top', 'left_mid', 'left_bottom', 'top_left',
                'top_mid', 'top_right', 'right_top', 'right_mid',
                'right_bottom', 'bottom_left', 'bottom_mid', 'bottom_right')
            index = values.index(self.bubb.arrow_pos)
            self.bubb.arrow_pos = values[(index + 1) % len(values)]
        #print('enter')
        pass

    def on_leave(self):
        if hasattr(self, 'bubb'):
            self.remove_widget(self.bubb)
            del self.bubb
        #print('leave')
        pass

Factory.register('HoverBehavior', cls=HoverBehavior)

if __name__=='__main__':
    from kivy.uix.floatlayout import FloatLayout
    from kivy.lang import Builder
    from kivy.uix.label import Label
    from kivy.base import runTouchApp
    class HoverLabel(Label, HoverBehavior):
        def on_enter(self, *args):
            print ("You are in, though this point", self.border_point)

        def on_leave(self, *args):
            print ("You left through this point", self.border_point)

    Builder.load_string('''
<HoverLabel>:
    text: "inside" if self.hovered else "outside"
    pos: 200,200
    size_hint: None, None
    size: 100, 30
    canvas.before:
        Color:
            rgb: 1,0,0
        Rectangle:
            size: self.size
            pos: self.pos
    ''')
    fl = FloatLayout()
    fl.add_widget(HoverLabel())
    runTouchApp(fl)