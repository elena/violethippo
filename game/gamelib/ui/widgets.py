import pyglet

from cocos.text import Label
from ninepatch import LabelNinepatch

from cocos.sprite import Sprite

from pyglet import gl

class Button(Sprite):
    def __init__(self, image, position, info, action):
        super(Button, self).__init__(image, position=position, anchor=(0, 0))
        self.info = info
        self.on_click = action


class TextButton(LabelNinepatch):
    def __init__(self, text, position, info, action,
            ninepatch='border-9p.png'):
        x, y = position
        super(TextButton, self).__init__(ninepatch, Label(text, x=x, y=y,
            color=(0, 0, 0, 255), anchor_x='left', anchor_y='bottom',
            font_name='Prototype'))
        self.info = info
        self.on_click = action


def bargraph_pattern(width):
    color1 = '%c%c%c%c' % (255, 255, 255, 255)
    color2 = '%c%c%c%c' % (0, 0, 0, 0)
    hw = width // 4
    data = color1 * hw * 3 + color2 * hw
    return pyglet.image.ImageData(width, 1, 'RGBA', data)


class Bargraph(Sprite):
    def __init__(self, size, value, **kw):
        image = bargraph_pattern(8)
        self._size = size
        self._value = value
        super(Bargraph, self).__init__(image, **kw)

        # have this sprite's image repeat
        gl.glBindTexture(self._texture.target, self._texture.id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
            gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
            gl.GL_REPEAT)

    @property
    def size(self):
        return self._size
    @size.setter
    def size(self, size):
        self._size = size
        self._update_position()

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
        self._update_position()

    def _update_position(self):
        # ignore rotation and scaling; set the tex coords at the same time as
        # vertexes
        img = self._texture
        if not self._visible:
            self._vertex_list.vertices[:] = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            x1 = int(self._x - img.anchor_x)
            y1 = int(self._y - img.anchor_y)
            w, h = self.size
            x2 = x1 + int(w * self.value)
            y2 = y1 + h
            self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]
            s2 = w * self.value / img.width
            self._vertex_list.tex_coords[:] = [0, 0, 0, s2, 0, 0, s2, 1, 0, 0, 1, 0]

if __name__ == '__main__':
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    director.init(width=1024, height=768)
    from cocos.scene import Scene
    from cocos.layer import Layer

    class Layer(Layer):
        is_event_handler = True
        def __init__(self):
            super(Layer, self).__init__()
            self.bg = Bargraph((100, 10), .3, position = (100, 100))
            self.add(self.bg)
        def on_text(self, text):
            if text == 'r':
                self.bg.color = (255, 0, 0)
            if text == 'g':
                self.bg.color = (0, 255, 0)
            if text == 'b':
                self.bg.color = (0, 0, 255)
        def on_text_motion(self, motion):
            if motion == pyglet.window.key.MOTION_LEFT:
                self.bg.value -= .1
            if motion == pyglet.window.key.MOTION_RIGHT:
                self.bg.value += .1

    director.run(Scene(Layer()))
