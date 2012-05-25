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

import re

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import sessionmaker

from terms.words import word, noun, thing, verb, exists, get_name
from terms.terms import Term, ObjectType
from terms import exceptions

NAME_PAT = re.compile(r'^([a-z][a-z_]*[a-z])[1-9]+$')


class Lexicon(object):

    def __init__(self, engine):
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        self.terms = {'word': word,
                      'noun': noun,
                      'verb': verb,
                      'thing': thing,
                      'exists': exists}
        wrd = Term('word', _bootstrap=True)
        self.session.add(wrd)
        self.add_word('noun', word, _commit=False)
        self.add_word('verb', word, _commit=False)
        self.add_word('thing', noun, _commit=False)
        self.add_word('exists', verb, _commit=False)
        self.session.commit()

    def add_word(self, name, word_type, _commit=True, **objs):
        try:
            term = self.get_term(name)
        except exceptions.TermNotFound:
            pass
        else:
            if term:
                raise exceptions.TermRepeated(name)
        objects = []
        for label, obj_type in objs.items():
            obj_tname = get_name(obj_type)
            obj_term = self.get_term(obj_tname)
            objects.append(ObjectType(label, obj_term))
        term_type = self.get_term(get_name(word_type))
        term = Term(name, ttype=term_type, objs=objects)
        self.session.add(term)
        if _commit:
            self.session.commit()
        if name in self.terms:
            return self.terms[name]
        if issubclass(word_type, noun):
            return self._make_noun(name, ntype=word_type)
        elif issubclass(word_type, thing):
            return self._make_name(name, word_type)
        elif issubclass(word_type, verb):
            return self._make_verb(name, vtype=word_type, objs=objs)

    def add_subword(self, name, super_words, _commit=True, **objs):
        try:
            term = self.get_term(name)
        except exceptions.TermNotFound:
            pass
        else:
            if term:
                raise exceptions.TermRepeated(name)
        term_bases = []
        if isinstance(super_words, word):
            super_words = (super_words,)
        objects = []
        for super_word in super_words:
            super_name = get_name(super_word)
            term_base = self.get_term(super_name)
            if hasattr(super_word, 'objs'):
                objects.extend(term_base.object_types)
                objs.update(super_word.objs)
            term_bases.append(term_base)
        for label, word_type in objs.items():
            type_name = get_name(word_type)
            objects.append(ObjectType(label, self.get_term(type_name)))
        term = Term(name, bases=term_bases, objs=objects)
        self.session.add(term)
        if _commit:
            self.session.commit()
        word_base = super_words[0]
        if issubclass(word_base, noun):
            return self._make_subnoun(name, bases=super_words)
        elif issubclass(word_base, thing):
            return self._make_noun(name, bases=super_words)
        elif issubclass(word_base, verb):
            return self._make_subverb(name, bases=super_words)
        elif issubclass(word_base, exists):
            return self._make_verb(name, bases=super_words, objs=objs)

    def get_word(self, name):
        if name in self.terms:
            return self.terms[name]
        term = self.get_term(name)
        word_type = self.terms[term.term_type.name]
        return self._make_name(name, word_type)

    def get_term(self, name):
        try:
            return self.session.query(Term).filter_by(name=name).one()
        except MultipleResultsFound:
            raise exceptions.TermRepeated()
        except NoResultFound:
            raise exceptions.TermNotFound()

    def _load_terms(self):
        terms = self.session.query(Term).all()
        for term in terms:
            type_name = term.types[0].name
            term_type = self.terms[type_name]
            if not issubclass(term_type, thing):
                term_types = [self.terms[ttype.name] for ttype in term.types]
                if issubclass(term_type, noun):
                    self._make_noun(type_name, term_types)
                elif issubclass(term_type, verb):
                    objects = dict([(obj.label, self.terms[obj.term_type.name])
                                                for obj in term.object_types])
                    self._make_verb(type_name, term_types, objects)

    def _make_noun(self, name, bases=None, ntype=None):
        if bases is None:
            bases = (thing,)
        elif isinstance(bases, word):
            bases = (bases,)
        if ntype is None:
            ntype = noun
        new = ntype(name, tuple(bases), {})
        self.terms[name] = new
        return new

    def _make_name(self, name, noun_=None):
        if noun_ is None:
            m = NAME_PAT.match(name)
            if m:
                noun_ = self.terms[m.group(1)]
                assert isinstance(noun_, noun)
            else:
                noun_ = thing
        new = noun_(name)
        self.terms[name] = new
        return new

    def _make_verb(self, name, bases=None, vtype=None, objs=None):
        if bases is None:
            bases = (exists,)
        elif bases is None:
            bases = ()
        elif isinstance(bases, verb):
            bases = (bases,)
        if objs is None:
            objs = {}
        if vtype is None:
            if bases:
                vtype = type(bases[0])
            else:
                vtype = verb
        new = vtype(name, tuple(bases), objs)
        self.terms[name] = new
        return new

    def _make_subverb(self, name, bases=None):
        if bases is None:
            bases = (verb,)
        new = word(name, tuple(bases), {})
        self.terms[name] = new
        return new

    def _make_subnoun(self, name, bases=None):
        if bases is None:
            bases = (noun,)
        new = word(name, tuple(bases), {})
        self.terms[name] = new
        return new