# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from __future__ import unicode_literals

from django.test import TestCase

from core.xmlrpclib import escape


class XmlrpclibTest(TestCase):
    def test_basic(self):
        self.assertEqual(escape('abc'), 'abc')
        self.assertEqual(escape('0123'), '0123')
        self.assertEqual(escape('@$!*'), '@$!*')

    def test_ascii_escape(self):
        self.assertEqual(escape('<>&'), '&lt;&gt;&amp;')
        self.assertEqual(escape('123<abc>456&def'), '123&lt;abc&gt;456&amp;def')

    def test_unicode_escape(self):
        self.assertEqual(escape('ъ'), '&#209;&#138;')  # http://en.wikipedia.org/wiki/%D0%AA
        self.assertEqual(escape('Д'), '&#208;&#148;')  # http://en.wikipedia.org/wiki/%D0%94
        self.assertEqual(escape('茶'), '&#232;&#140;&#182;')  # http://en.wiktionary.org/wiki/%E8%8C%B6
        self.assertEqual(escape('Λ'), '&#206;&#155;')  # http://en.wikipedia.org/wiki/Lambda

    def test_mixed(self):
        self.assertEqual(escape('ab&Λdef'), 'ab&amp;&#206;&#155;def')

    def test_tricks(self):
        self.assertEqual(escape('&amp;'), '&amp;amp;')
