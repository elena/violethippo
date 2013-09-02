#! /usr/bin/env python

import pyglet
pyglet.resource.path.append('data')
pyglet.resource.reindex()

from gamelib import main
main.main()
