# -*- coding: utf-8 -*-
from cocos.scene import Scene
from gamelib.ui.splash import splash_color, splash_control
from cocos.actions import AccelDeccelAmplitude, Waves3D


main_scene = Scene(splash_color, splash_control)
main_scene.do(
    AccelDeccelAmplitude( Waves3D(waves=12, amplitude=30, duration=25,
                                  grid=(32,24)), rate=2.0 ),
)