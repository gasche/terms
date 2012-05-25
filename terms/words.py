# Copyright (c) 2007-2012 by Enrique Pérez Arnaud <enriquepablo@gmail.com>
#
# This file is part of the terms project.
# https://github.com/enriquepablo/terms
#
# The terms project is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The terms project is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any part of the terms project.
# If not, see <http://www.gnu.org/licenses/>.

word = type


class noun(word, metaclass=word):
    """ """


class thing(word, metaclass=noun):
    """ """

    def __new__(cls, name):
        """ """
        return super(thing, cls).__new__(cls, name, (), {})

    def __init__(self, name):
        """ """
        return super(thing, self).__init__(name, (), {})


class verb(word, metaclass=word):
    """ """
    def __new__(cls, classname, bases, newdict):
        return super(verb, cls).__new__(cls, classname, bases, {'objs': {}})

    def __init__(self, classname, bases, newdict):
        self.objs = newdict


class exists(word, metaclass=verb):
    """ """

def _new_exists(cls, classname, bases, newdict):
    labels = sorted(list(cls.objs))
    name = [cls.__name__]
    for label in labels:
        obj = newdict.get(label, None)
        if obj:
            name.append(label)
            name.append(get_name(obj))
    name = '__'.join(name)
    return super(exists, cls).__new__(cls, name, bases, newdict)

def _init_exists(self, classname, bases, newdict):
    for label, obj in newdict.items():
        setattr(self, '_' + label, obj)

def _getattr_exists(self, label):
    if not label.startswith('_'):
        label = '_' + label
    return super(exists, self).__getattr__(label)

exists.__new__ = _new_exists
exists.__init__ = _init_exists
exists.__getattr__ = _getattr_exists
exists.objs = {'subject': word}


def get_name(w):
    if w is type:
        return 'word'
    return w.__name__


def make_pred(verb_, **objs):
    name = get_name(verb_)
    obj_list = list(objs.items())
    obj_list = sorted(obj_list, key=lambda x: x[0])
    for label, obj in obj_list:
        name += '__' + label + '__' + get_name(obj)
    return verb_(name, (), objs)
