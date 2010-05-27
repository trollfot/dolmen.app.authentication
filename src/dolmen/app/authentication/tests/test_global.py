# -*- coding: utf-8 -*-

import unittest
import zope.component

from dolmen.app.authentication import tests
from zope.app.wsgi.testlayer import BrowserLayer
from zope.interface import Interface
from zope.testing import doctest


class DolmenApplicationAuthLayer(BrowserLayer):

    def setUp(self):
        BrowserLayer.setUp(self)
        zope.component.hooks.setHooks()
 
    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()
        BrowserLayer.tearDown(self)


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt',
        globs={'__name__': 'dolmen.app.authentication'},
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    readme.layer = DolmenApplicationAuthLayer(tests)
    suite.addTest(readme)
    return suite
