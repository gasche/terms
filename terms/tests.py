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

import os
import re

from terms.network import Network
from terms.compiler import KB
from terms.log import here, logger


def test_terms(): # test generator
    # read contents of terms/
    # feed each content to run_npl
    d = os.path.join(here, 'examples')
    files = os.listdir(d)
#    yield run_npl, '/home/eperez/virtualenvs/ircbot/src/nl/nl/npl_tests/lists.npl'
    for f in files:
        if f.endswith('.trm'):
            network = Network()
            kb = KB(network,
                    lex_optimize=False,
                    yacc_optimize=False,
                    yacc_debug=True)
            yield run_terms, kb, os.path.join(d, f)


def run_terms(kb, fname):
    # open file, read lines
    # tell asserions
    # compare return of questions with provided output
    with open(fname) as f:
        resp, buff = None, ''
        for sen in f.readlines():
            logger.info(sen)
            sen = sen.strip()
            if resp is not None:
                sen = sen.strip('.')
                logger.info('%s match %s' % (sen, resp))
                assert re.compile(sen).match(resp)
                resp = None
            elif sen and not sen.startswith('#'):
                buff += ' ' + sen
                if buff.endswith('.'):
                    logger.info(kb.parse(buff))
                    buff = ''
                elif buff.endswith('?'):
                    resp = kb.parse(buff)
                    buff = ''
