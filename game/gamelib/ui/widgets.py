
from cocos.text import Label
from ninepatch import LabelNinepatch

from cocos.sprite import Sprite


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
            color=(0, 0, 0, 255), anchor_x='left', anchor_y='bottom'))
        self.info = info
        self.on_click = action
