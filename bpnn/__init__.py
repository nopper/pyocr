# -*- coding: utf-8 -*-
# Copyright (C) 2009 Francesco Piccinno
#
# Author: Francesco Piccinno <stack.box@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from random import randint
from network import Network

def test_xor():
    n = Network(2, 4, 1)
    train = (
        ([0, 0], [0]),
        ([1, 1], [0]),
        ([0, 1], [1]),
        ([1, 0], [1]),
    )

    for i in xrange(20000):
        inp, out = train[randint(0, 3)]
        n.train(inp, out)

    for inp, out in train:
        assert round(n.test(inp)[0]) == out[0]

def test_bindec():
    n = Network(4, 6, 16)
    train = {}

    for i in xrange(16):
        bstr = bin(i)[2:]
        bstr = '0' * (4 - len(bstr)) + bstr

        inp = map(int, [c for c in bstr])

        out = [0] * 16
        out[i] = 1

        train[i] = (inp, out)

    for i in xrange(100000):
        n.train(*train[randint(0, 15)])

    for k, (inp, out) in train.items():
        ret = n.test(inp)
        assert ret.index(max(ret)) == k
