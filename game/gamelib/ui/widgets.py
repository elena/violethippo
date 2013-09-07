import pyglet

from cocos.text import Label
from ninepatch import LabelNinepatch

from cocos.sprite import Sprite
from cocos.batch import BatchNode

from pyglet import gl

class Button(Sprite):
    def __init__(self, image, position, info, action, **kw):
        super(Button, self).__init__(image, position=position, anchor=(0, 0))
        for k, v in kw.items():
            setattr(self, k, v)
        self.info = info
        self.on_click = action


class TextButton(LabelNinepatch):
    def __init__(self, text, position, info, action,
                 color=(255, 255, 255, 255), **kw):
        x, y = position
        ninepatch = kw.pop('ninepatch', 'border-9p.png')
        super(TextButton, self).__init__(ninepatch, Label(text, x=x, y=y,
            color=color, anchor_x='left', anchor_y='bottom',
            font_name='Prototype'))
        for k, v in kw.items():
            setattr(self, k, v)
        self.info = info
        self.on_click = action


_bg_textures = {}
def dashed_pattern(width):
    if width in _bg_textures:
        return _bg_textures[width]
    color1 = '%c%c%c%c' % (255, 255, 255, 255)
    color2 = '%c%c%c%c' % (0, 0, 0, 0)
    hw = width // 4
    data = color1 * hw * 3 + color2 * hw
    im = pyglet.image.ImageData(width, 1, 'RGBA', data)
    # have this image repeat
    gl.glBindTexture(im.texture.target, im.texture.id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
        gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
        gl.GL_REPEAT)
    return im

def solid_pattern():
    if 'solid' in _bg_textures:
        return _bg_textures['solid']
    data = '%c%c%c%c' % (255, 255, 255, 255)
    im = pyglet.image.ImageData(1, 1, 'RGBA', data)
    # have this image repeat
    gl.glBindTexture(im.texture.target, im.texture.id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
        gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
        gl.GL_REPEAT)
    return im


class Bargraph(Sprite):
    def __init__(self, size, value, **kw):
        style = kw.pop('style', 'dashed')
        if style == 'dashed':
            image = dashed_pattern(8)
        else:
            image = solid_pattern()
        self._size = size
        self._value = value
        super(Bargraph, self).__init__(image, **kw)

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

    def _update_position(self, x_offset=0, s_offset=0):
        # ignore rotation and scaling; set the tex coords at the same time as
        # vertexes
        img = self._texture
        if not self._visible:
            self._vertex_list.vertices[:] = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            x1 = int(self._x - img.anchor_x) + x_offset
            y1 = int(self._y - img.anchor_y)
            w, h = self.size
            x2 = x1 + int(w * self.value)
            y2 = y1 + h
            self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]
            s1 = s_offset
            s2 = s1 + int(w * self.value) / float(img.width)
            self._vertex_list.tex_coords[:] = [
                s1, 0, 0,
                s2, 0, 0,
                s2, 1, 0,
                s1, 1, 0
            ]


class MultipleBargraph(BatchNode):
    def __init__(self, size, values, **kw):
        super(MultipleBargraph, self).__init__()
        self._size = size
        self.position = kw.pop('position', (0,0))
        w, h = size
        style = kw.pop('style', 'dashed')
        self.graphs = [Bargraph((w//3, h), value, style=style)
            for value in values]
        if 'colors' in kw:
            for color, graph in zip(kw['colors'], self.graphs):
                graph.color = color
        map(self.add, self.graphs)
        self._values = values
        self._update_graphs()

    @property
    def values(self):
        return self._values
    @values.setter
    def values(self, values):
        assert len(values) == len(self._values)
        self._values = values
        self._update_graphs()

    def _update_graphs(self):
        x_offset = s_offset = 0
        for value, graph in zip(self._values, self.graphs):
            graph._value = value
            graph._x, graph._y = self.position
            graph._update_position(x_offset, s_offset)
            x_offset += int(graph.size[0] * value)
            s_offset += int(graph.size[0] * value) / float(graph._texture.width)


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
            self.bg = Bargraph((100, 8), .3, position=(0, 0))
            self.add(self.bg)
            self.mbg = MultipleBargraph((100, 8), (.8, .9, 1), position=(0, 8),
                colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], style='solid')
            self.add(self.mbg)
            self.active = 0
        def on_text(self, text):
            if text == 'r':
                self.bg.color = (255, 0, 0)
            if text == 'g':
                self.bg.color = (0, 255, 0)
            if text == 'b':
                self.bg.color = (0, 0, 255)
            if text in '0123':
                self.active = int(text)
        def on_text_motion(self, motion):
            if motion == pyglet.window.key.MOTION_LEFT:
                if self.active == 0:
                    self.bg.value -= .1
                else:
                    values = list(self.mbg.values)
                    values[self.active - 1] -= .1
                    self.mbg.values = values
            if motion == pyglet.window.key.MOTION_RIGHT:
                if self.active == 0:
                    self.bg.value += .1
                else:
                    values = list(self.mbg.values)
                    values[self.active - 1] += .1
                    self.mbg.values = values

    director.run(Scene(Layer()))
