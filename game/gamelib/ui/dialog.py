import pyglet

from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.sprite import Sprite
from cocos.rect import Rect

from ninepatch import NinePatch

class ChoiceLayer(Layer):
    is_event_handler = True

    def __init__(self, title, choices, callback):
        super(ChoiceLayer, self).__init__()
        self.callback = callback
        self.add(ColorLayer(255, 255, 255, 200), z=-2)
        w, h = director.get_window_size()

        but = Label(title, color=(0, 0, 0, 255), x=w//2,
            anchor_x='center', y=h-256, font_size=24)
        x1 = but.element.x - but.element.content_width // 2
        y1 = but.element.y
        x2 = but.element.x + but.element.content_width // 2
        y2 = but.element.y + but.element.content_height
        self.add(but)

        self.choice_buts = []
        y = h-256 - 64
        for choice in choices:
            but = Label(choice, color=(0, 0, 0, 255), x=w//2,
                anchor_x='center', y=y, font_size=20)
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
        self.parent.update()
        self.kill()
        return True

    def on_key_press(self, *args):
        self.callback = None
        self.kill()
        return True
