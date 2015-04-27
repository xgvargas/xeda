# -*- coding: utf-8 -*-


class meta():
    pass


def init():
    global meta
    import xhelper
    meta = xhelper.readYamlConfig('config.yaml')

def save():
    pass
