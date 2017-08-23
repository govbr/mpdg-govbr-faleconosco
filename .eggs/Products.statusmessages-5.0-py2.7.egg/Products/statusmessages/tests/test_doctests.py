# -*- coding: utf-8 -*-
from doctest import DocTestSuite
from unittest import TestSuite


test_list = (
    DocTestSuite('Products.statusmessages.adapter'),
    DocTestSuite('Products.statusmessages.message'),
)


def test_suite():
    return TestSuite(test_list)
