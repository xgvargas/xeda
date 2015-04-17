# -*- coding: utf-8 -*-

from __future__ import print_function

"""Set of unrelated helper functions."""

def readYamlConfig(filename):
    """Read in a configuration file in YAML format.
    Returns an object with all configuration and respecting hierarchy.
    Also, an extra member in this object called '_d', contains the same configuration in DICT form."""
    import yaml
    try:
        class Dict2Obj(object):
            def __init__(self, d, first=True):
                for a, b in d.items():
                    if isinstance(b, (list, tuple)):
                        setattr(self, a, [Dict2Obj(x, False) if isinstance(x, dict) else x for x in b])
                    else:
                        setattr(self, a, Dict2Obj(b, False) if isinstance(b, dict) else b)
                    if first:
                        setattr(self, '_d', d)

        with open(filename, 'r') as fh:
            cfg = Dict2Obj(yaml.load(fh.read()))
    except IOError:
        print("Oops! File '{}' was not found!".format(filename))
        return None
    except yaml.parser.ParserError as e:
        print("Oops! File '{}' has invalid YAML!".format(filename))
        print(str(e))
        return None
    except Exception as e:
        print(type(e))
        return None

    return cfg
