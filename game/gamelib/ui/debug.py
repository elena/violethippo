
import pyglet
from cocos.director import director
from cocos.layer import Layer, ColorLayer, PythonInterpreterLayer
from pyglet.text.layout import IncrementalTextLayout


# we can maybe turn this on later...
# class DebugLayer(PythonInterpreterLayer):
#     def on_key_press(self, symbol, modifiers):
#         if not self.visible:
#             return False
#         if symbol == pyglet.window.key.GRAVE:
#             self.visible = False
#             return True
#         return super(DebugLayer, self).on_key_press(symbol, modifiers)

#     def on_text(self, symbol):
#         if not self.visible:
#             return False
#         if symbol == '`':
#             return True
#         return super(DebugLayer, self).on_text(symbol)

#     def on_text_motion(self, motion):
#         if not self.visible:
#             return False
#         return super(DebugLayer, self).on_text_motion(motion)


# override standard pyglet DocumentLabel so we're scrollable
# TODO batch me!
class DocumentLabel(IncrementalTextLayout):
    def __init__(self, document=None,
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 multiline=False, dpi=None, batch=None, group=None):
        super(DocumentLabel, self).__init__(document, width=width,
            height=height, multiline=multiline, dpi=dpi, batch=batch,
            group=group)
        self._x = x
        self._y = y
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self._update()

    def _get_text(self):
        return self.document.text
    def _set_text(self, text):
        self.document.text = text
    text = property(_get_text, _set_text)


class DebugLayer(Layer):
    is_event_handler = True
    def __init__(self):
        super(DebugLayer, self).__init__()
        w, h = director.get_window_size()
        self.add(ColorLayer(245, 244, 240, 200), z=-1)
        self.lines = ["hi, I'm the console!\n"]
        self.document = pyglet.text.decode_text('')
        self.label = DocumentLabel(self.document, width=w-20, height=h-20,
             y=h-10, x=10, anchor_y='top', multiline=True)

    def draw(self):
        self.label.draw()

    def write(self, text):
        self.lines.append(text)
        if len(self.lines) > 1000:
            self.lines.pop(0)
        if self.visible:
            self.label.text = '\n'.join(self.lines)
            self.label.ensure_line_visible(self.label.get_line_count()-1)

    def toggle_visible(self):
        self.visible = not self.visible
        if self.visible:
            self.label.text = '\n'.join(self.lines)
            self.label.ensure_line_visible(self.label.get_line_count()-1)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.GRAVE:
            self.toggle_visible()
            return True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.label.view_x -= scroll_x
        self.label.view_y += scroll_y * 16
