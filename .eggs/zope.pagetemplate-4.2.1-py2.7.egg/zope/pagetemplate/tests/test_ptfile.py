##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests of PageTemplateFile.
"""
import os
import tempfile
import unittest

import six
from zope.pagetemplate.pagetemplatefile import PageTemplateFile


class TypeSniffingTestCase(unittest.TestCase):

    TEMPFILENAME = tempfile.mktemp()

    def tearDown(self):
        if os.path.exists(self.TEMPFILENAME):
            os.unlink(self.TEMPFILENAME)

    def get_pt(self, text):
        f = open(self.TEMPFILENAME, "wb")
        f.write(text)
        f.close()
        pt = PageTemplateFile(self.TEMPFILENAME)
        pt.read()
        return pt

    def check_content_type(self, text, expected_type):
        pt = self.get_pt(text)
        self.assertEqual(pt.content_type, expected_type)

    def test_sniffer_xml_ascii(self):
        self.check_content_type(
            b"<?xml version='1.0' encoding='ascii'?><doc/>",
            "text/xml")
        self.check_content_type(
            b"<?xml\tversion='1.0' encoding='ascii'?><doc/>",
            "text/xml")

    def test_sniffer_xml_utf8(self):
        # w/out byte order mark
        self.check_content_type(
            b"<?xml version='1.0' encoding='utf-8'?><doc/>",
            "text/xml")
        self.check_content_type(
            b"<?xml\tversion='1.0' encoding='utf-8'?><doc/>",
            "text/xml")
        # with byte order mark
        self.check_content_type(
            b"\xef\xbb\xbf<?xml version='1.0' encoding='utf-8'?><doc/>",
            "text/xml")
        self.check_content_type(
            b"\xef\xbb\xbf<?xml\tversion='1.0' encoding='utf-8'?><doc/>",
            "text/xml")

    def test_sniffer_xml_utf16_be(self):
        # w/out byte order mark
        self.check_content_type(
            b"\0<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")
        self.check_content_type(
            b"\0<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")
        # with byte order mark
        self.check_content_type(
            b"\xfe\xff"
            b"\0<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")
        self.check_content_type(
            b"\xfe\xff"
            b"\0<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'"
            b"\0 \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>"
            b"\0<\0d\0o\0c\0/\0>",
            "text/xml")

    def test_sniffer_xml_utf16_le(self):
        # w/out byte order mark
        self.check_content_type(
            b"<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\n",
            "text/xml")
        self.check_content_type(
            b"<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\0",
            "text/xml")
        # with byte order mark
        self.check_content_type(
            b"\xff\xfe"
            b"<\0?\0x\0m\0l\0 \0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\0",
            "text/xml")
        self.check_content_type(
            b"\xff\xfe"
            b"<\0?\0x\0m\0l\0\t\0v\0e\0r\0s\0i\0o\0n\0=\0'\01\0.\0000\0'\0"
            b" \0e\0n\0c\0o\0d\0i\0n\0g\0=\0'\0u\0t\0f\0-\08\0'\0?\0>\0"
            b"<\0d\0o\0c\0/\0>\0",
            "text/xml")

    HTML_PUBLIC_ID = "-//W3C//DTD HTML 4.01 Transitional//EN"
    HTML_SYSTEM_ID = "http://www.w3.org/TR/html4/loose.dtd"

    def test_sniffer_html_ascii(self):
        self.check_content_type(
            ("<!DOCTYPE html [ SYSTEM '%s' ]><html></html>"
            % self.HTML_SYSTEM_ID).encode("utf-8"),
            "text/html")
        self.check_content_type(
            b"<html><head><title>sample document</title></head></html>",
            "text/html")

    # TODO: This reflects a case that simply isn't handled by the
    # sniffer; there are many, but it gets it right more often than
    # before.
    def donttest_sniffer_xml_simple(self):
        self.check_content_type("<doc><element/></doc>",
                                "text/xml")

    def test_html_default_encoding(self):
        pt = self.get_pt(
            b"<html><head><title>"
            # 'Test' in russian (utf-8)
            b"\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82"
            b"</title></head></html>")
        rendered = pt()
        self.assertTrue(isinstance(rendered, six.text_type))
        self.assertEqual(rendered.strip(),
            six.u("<html><head><title>"
                  "\u0422\u0435\u0441\u0442"
                  "</title></head></html>"))

    def test_html_encoding_by_meta(self):
        pt = self.get_pt(
            b"<html><head><title>"
            # 'Test' in russian (windows-1251)
            b"\xd2\xe5\xf1\xf2"
            b'</title><meta http-equiv="Content-Type"'
            b' content="text/html; charset=windows-1251">'
            b"</head></html>")
        rendered = pt()
        self.assertTrue(isinstance(rendered, six.text_type))
        self.assertEqual(rendered.strip(),
            six.u("<html><head><title>"
                  "\u0422\u0435\u0441\u0442"
                  "</title></head></html>"))

    def test_xhtml(self):
        pt = self.get_pt(
            b"<html><head><title>"
            # 'Test' in russian (windows-1251)
            b"\xd2\xe5\xf1\xf2"
            b'</title><meta http-equiv="Content-Type"'
            b' content="text/html; charset=windows-1251"/>'
            b"</head></html>")
        rendered = pt()
        self.assertTrue(isinstance(rendered, six.text_type))
        self.assertEqual(rendered.strip(),
            six.u("<html><head><title>"
                  "\u0422\u0435\u0441\u0442"
                  "</title></head></html>"))



def test_suite():
    return unittest.makeSuite(TypeSniffingTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
