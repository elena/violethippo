
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.sprite import Sprite
from cocos.rect import Rect


class ChoiceLayer(Layer):
    is_event_handler = True
    def __init__(self, title, choices, callback):
        super(ChoiceLayer, self).__init__()
        self.callback = callback
        self.add(ColorLayer(0, 0, 0, 200))
        w, h = director.get_window_size()

        self.add(Label(title, color=(200, 200, 200, 255), x=w//2,
            anchor_x='center', y=h-128, font_size=30))

        self.choice_buts = []
        y = h-256
        for choice in choices:
            but = Label(choice, color=(200, 200, 200, 255), x=w//2,
                anchor_x='center', y=y, font_size=20)
            y -= 64
            self.add(but)
            but.rect = Rect(but.element.x, but.element.y,
                but.element.content_width, but.element.content_height)
            self.choice_buts.append(but)

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
