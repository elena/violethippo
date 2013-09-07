import pyglet

from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.sprite import Sprite
from cocos.rect import Rect

from ninepatch import NinePatch


class OkLayer(Layer):
    '''A Layer that asks a question and consumes keyboard and mouse clicks to
    dismiss.

    The title is the message you wish to convey; the explanation is additional
    optional text that may go over multiple lines. If the explanation is
    provided you may also specify the width of the dialog (default 400px).

    The callback is invoked with the parent scene (the "ui") when the dialog
    is dismissed.
    '''
    is_event_handler = True

    def __init__(self, title, callback, explanation=None, width=400):
        super(OkLayer, self).__init__()
        self.callback = callback
        self.add(ColorLayer(255, 255, 255, 200), z=-2)
        w, h = director.get_window_size()

        y = h - 256
        but = Label(title, color=(0, 0, 0, 255), x=w//2,
            anchor_x='center', y=y, font_size=24)
        x1 = but.element.x - but.element.content_width // 2
        y1 = but.element.y
        x2 = but.element.x + but.element.content_width // 2
        y2 = but.element.y + but.element.content_height
        self.add(but)
        y -= but.element.content_height + 10

        if explanation:
            but = Label(explanation, multiline=True, color=(0, 0, 0, 255),
                x=w//2, width=width, anchor_x='center', anchor_y='top', y=y,
                font_size=14, align='center',
            font_name='Prototype')
            self.add(but)
            x = but.element.x - width // 2
            x1 = min(x, x1)
            y1 = min(but.element.y, y1)
            x2 = max(but.element.x + width // 2, x2)
            y2 = max(but.element.y + but.element.content_height, y2)
            y -= but.element.content_height + 10

        but = Label('(click or press a key to dismiss)', color=(0, 0, 0, 255),
            x=w//2, anchor_x='center', anchor_y='bottom', y=y-32, font_size=12,
            font_name='Prototype')
        self.add(but)
        x = but.element.x - but.element.content_width // 2
        x1 = min(x, x1)
        y1 = min(but.element.y, y1)
        x2 = max(but.element.x + but.element.content_width // 2, x2)
        y2 = max(but.element.y + but.element.content_height, y2)
        but.rect = Rect(x, but.element.y, but.element.content_width,
            but.element.content_height)

        self.patch_dimensions = (x1, y1, x2-x1, y2-y1)

        self.ninepatch = NinePatch(pyglet.resource.image('border-9p.png'))

    def draw(self):
        self.ninepatch.draw_around(*self.patch_dimensions)

    def on_mouse_press(self, x, y, button, modifiers):
        if Rect(*self.patch_dimensions).contains(x, y):
            self.callback(self.parent)
        self.callback = None
        self.kill()
        return True

    def on_key_press(self, *args):
        self.callback(self.parent)
        self.callback = None
        self.kill()
        return True

class ChoiceLayer(Layer):
    '''A Layer that asks a question with a choice of answers and consumes
    keyboard and mouse clicks to dismiss.

    Supply a 'cancel' choice if you wish that to be an option for the user.

    The title is the message you wish to convey; the explanation is additional
    optional text that may go over multiple lines. If the explanation is
    provided you may also specify the width of the dialog (default 400px).

    The callback is invoked with the parent scene (the "ui") and the choice
    selected by the user when the dialog is dismissed.
    '''
    is_event_handler = True

    def __init__(self, title, choices, callback, explanation=None, width=400):
        super(ChoiceLayer, self).__init__()
        self.callback = callback
        self.add(ColorLayer(255, 255, 255, 100), z=-2)
        w, h = director.get_window_size()

        y = h - 256
        but = Label(title, color=(0, 0, 0, 255), x=w//2,
            anchor_x='center', y=y, font_size=24)
        x1 = but.element.x - but.element.content_width // 2
        y1 = but.element.y
        x2 = but.element.x + but.element.content_width // 2
        y2 = but.element.y + but.element.content_height
        self.add(but)
        y -= but.element.content_height + 10

        if explanation:
            but = Label(explanation, multiline=True, color=(0, 0, 0, 255),
                x=w//2, width=width, anchor_x='center', anchor_y='top', y=y,
                font_size=14, align='center',
            font_name='Prototype')
            self.add(but)
            x = but.element.x - width // 2
            x1 = min(x, x1)
            y1 = min(but.element.y, y1)
            x2 = max(but.element.x + width // 2, x2)
            y2 = max(but.element.y + but.element.content_height, y2)
            y -= but.element.content_height + 10

        y -= 32

        self.choice_buts = []
        for choice in choices:
            but = Label(choice, color=(0, 0, 0, 255), x=w//2,
                anchor_x='center',  anchor_y='bottom', y=y, font_size=20,
            font_name='Prototype')
            y -= 32
            self.add(but, z=1)
            self.choice_buts.append(but)
            x = but.element.x - but.element.content_width // 2
            x1 = min(x, x1)
            y1 = min(but.element.y, y1)
            x2 = max(but.element.x + but.element.content_width // 2, x2)
            y2 = max(but.element.y + but.element.content_height, y2)
            but.rect = Rect(x, but.element.y, but.element.content_width,
                but.element.content_height)

        self.patch_dimensions = (x1, y1, x2-x1, y2-y1)

        self.ninepatch = NinePatch(pyglet.resource.image('border-9p.png'))

    def draw(self):
        self.ninepatch.draw_around(*self.patch_dimensions)

    def on_mouse_press(self, x, y, button, modifiers):
        for but in self.choice_buts:
            if but.rect.contains(x, y):
                self.callback(self.parent, but.element.text)
        self.callback = None
        self.kill()
        return True

    def on_key_press(self, *args):
        self.callback = None
        self.kill()
        return True


if __name__ == '__main__':
    import sys
    import pyglet
    pyglet.resource.path.append('../../data')
    pyglet.resource.reindex()

    from cocos.director import director
    from cocos.scene import Scene
    director.init(width=1024, height=768)

    def cb(*args):
        print 'callback', args

    if 'explain' in sys.argv:
        explanation = 'a somewhat long descrition and longish '\
            'explanation of stuffs'
    else:
        explanation = None

    if 'ok' in sys.argv:
        director.run(Scene(OkLayer('Information', cb, explanation)))
    if 'ask' in sys.argv:
        director.run(Scene(ChoiceLayer('Question', ['the', 'many', 'options'],
            cb, explanation)))
