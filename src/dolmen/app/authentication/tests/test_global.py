# -*- coding: utf-8 -*-

import unittest
import zope.component

from dolmen.app.authentication import tests
from zope.component.testlayer import ZCMLFileLayer
from zope.interface import Interface
from zope.testing import doctest


class DolmenApplicationAuthLayer(ZCMLFileLayer):

    def setUp(self):
        ZCMLFileLayer.setUp(self)
        zope.component.hooks.setHooks()
 
    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()
        ZCMLFileLayer.tearDown(self)


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt',
        globs={'__name__': 'dolmen.app.authentication'},
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    readme.layer = DolmenApplicationAuthLayer(tests)
    suite.addTest(readme)
    return suite
