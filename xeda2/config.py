# -*- coding: utf-8 -*-

import xhelper


class meta():
    pass


def init():
    global meta
    meta = xhelper.readYamlConfig('config.yaml')

def save():
    pass
