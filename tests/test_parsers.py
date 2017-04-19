#!/usr/bin/python

"""Test the __init__.py module"""

import os
import rpm
import unittest

import koji

class INITTestCase(unittest.TestCase):
    """Main test case container"""

    def test_parse_NVR(self):
        """Test the parse_NVR method"""

        self.assertRaises(AttributeError, koji.parse_NVR, None)
        self.assertRaises(AttributeError, koji.parse_NVR, 1)
        self.assertRaises(AttributeError, koji.parse_NVR, {})
        self.assertRaises(AttributeError, koji.parse_NVR, [])
        self.assertRaises(koji.GenericError, koji.parse_NVR, "")
        self.assertRaises(koji.GenericError, koji.parse_NVR, "foo")
        self.assertRaises(koji.GenericError, koji.parse_NVR, "foo-1")
        self.assertRaises(koji.GenericError, koji.parse_NVR, "foo-1-")
        self.assertRaises(koji.GenericError, koji.parse_NVR, "foo--1")
        self.assertRaises(koji.GenericError, koji.parse_NVR, "--1")
        ret = koji.parse_NVR("foo-1-2")
        self.assertEqual(ret['name'], "foo")
        self.assertEqual(ret['version'], "1")
        self.assertEqual(ret['release'], "2")
        self.assertEqual(ret['epoch'], "")
        ret = koji.parse_NVR("12:foo-1-2")
        self.assertEqual(ret['name'], "foo")
        self.assertEqual(ret['version'], "1")
        self.assertEqual(ret['release'], "2")
        self.assertEqual(ret['epoch'], "12")

    def test_parse_NVRA(self):
        """Test the parse_NVRA method"""

        self.assertRaises(AttributeError, koji.parse_NVRA, None)
        self.assertRaises(AttributeError, koji.parse_NVRA, 1)
        self.assertRaises(AttributeError, koji.parse_NVRA, {})
        self.assertRaises(AttributeError, koji.parse_NVRA, [])
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo-1")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo-1-")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo--1")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "--1")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo-1-1")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo-1-1.")
        self.assertRaises(koji.GenericError, koji.parse_NVRA, "foo-1.-1")
        ret = koji.parse_NVRA("foo-1-2.i386")
        self.assertEqual(ret['name'], "foo")
        self.assertEqual(ret['version'], "1")
        self.assertEqual(ret['release'], "2")
        self.assertEqual(ret['epoch'], "")
        self.assertEqual(ret['arch'], "i386")
        self.assertEqual(ret['src'], False)
        ret = koji.parse_NVRA("12:foo-1-2.src")
        self.assertEqual(ret['name'], "foo")
        self.assertEqual(ret['version'], "1")
        self.assertEqual(ret['release'], "2")
        self.assertEqual(ret['epoch'], "12")
        self.assertEqual(ret['arch'], "src")
        self.assertEqual(ret['src'], True)

    def test_check_NVR(self):
        """Test the check_NVR function"""
        good = [
            "name-version-release",
            "fnord-5.23-17",
            {'name': 'foo', 'version': '2.2.2', 'release': '1.1'},
            ]
        bad = [
            "this is not an NVR",
            {'name': 'foo', 'version': '2.2.2-a', 'release': '1.1'},
            {'name': 'foo', 'version': '2.2.2', 'release': '1.1-b'},
            ]
        for value in good:
            self.assertEqual(koji.check_NVR(value), True)
        for value in bad:
            self.assertEqual(koji.check_NVR(value), False)
            self.assertRaises(koji.GenericError,
                              koji.check_NVR, value, strict=True)

    def test_check_NVRA(self):
        """Test the check_NVRA function"""
        good = [
            "name-version-release.arch",
            "fnord-5.23-17.x86_64",
            {'name': 'foo', 'version': '2.2.2', 'release': '1.1',
                'arch': 'i686'},
            ]
        bad = [
            "this is not an NVRA",
            "fnord-5.23-17",
            {'name': 'foo', 'version': '2.2.2-a', 'release': '1.1',
                'arch': 'ppc64'},
            {'name': 'foo', 'version': '2.2.2', 'release': '1.1-b',
                'arch': 'x86_64'},
            {'name': 'foo', 'version': '2.2.2', 'release': '1.1',
                'arch': 'x.86.64'},
            ]
        for value in good:
            self.assertEqual(koji.check_NVRA(value), True)
        for value in bad:
            self.assertEqual(koji.check_NVRA(value), False)
            self.assertRaises(koji.GenericError,
                              koji.check_NVRA, value, strict=True)


class HeaderTestCase(unittest.TestCase):
    rpm_path = os.path.join(os.path.dirname(__file__), 'data/rpms/test-deps-1-1.fc24.x86_64.rpm')
    rpmdir = os.path.join(os.path.dirname(__file__), 'data/rpms')

    def setUp(self):
        self.fd = open(self.rpm_path)

    def tearDown(self):
        self.fd.close()

    def test_get_rpm_header(self):
        self.assertRaises(IOError, koji.get_rpm_header, 'nonexistent_path')
        self.assertRaises(AttributeError, koji.get_rpm_header, None)
        self.assertIsInstance(koji.get_rpm_header(self.rpm_path), rpm.hdr)
        self.assertIsInstance(koji.get_rpm_header(self.fd), rpm.hdr)
        # TODO:
        # test ts

    def test_get_header_fields(self):
        # incorrect
        self.assertRaises(IOError, koji.get_header_fields, 'nonexistent_path', [])
        self.assertRaises(koji.GenericError, koji.get_header_fields, self.rpm_path, 'nonexistent_header')
        self.assertEqual(koji.get_header_fields(self.rpm_path, []), {})

        # correct
        self.assertEqual(['REQUIRES'], koji.get_header_fields(self.rpm_path, ['REQUIRES']).keys())
        self.assertEqual(['PROVIDES', 'REQUIRES'], sorted(koji.get_header_fields(self.rpm_path, ['REQUIRES', 'PROVIDES'])))
        hdr = koji.get_rpm_header(self.rpm_path)
        self.assertEqual(['REQUIRES'], koji.get_header_fields(hdr, ['REQUIRES']).keys())


    def test_get_header_field_src(self):
        srpm = os.path.join(self.rpmdir, 'test-src-1-1.fc24.src.rpm')

        # without src_arch, should return the build arch (x86_64)
        data =  koji.get_header_fields(srpm, ['arch'])
        self.assertEqual(data['arch'], 'x86_64')

        # eith src_arch, should return src
        data =  koji.get_header_fields(srpm, ['arch'], src_arch=True)
        self.assertEqual(data['arch'], 'src')


    def test_get_header_field_nosrc(self):
        srpm1 = os.path.join(self.rpmdir, 'test-nosrc-1-1.fc24.nosrc.rpm')
        srpm2 = os.path.join(self.rpmdir, 'test-nopatch-1-1.fc24.nosrc.rpm')

        # without src_arch, should return the build arch (x86_64)
        for srpm in srpm1, srpm2:
            data =  koji.get_header_fields(srpm, ['arch'])
            self.assertEqual(data['arch'], 'x86_64')

        # eith src_arch, should return nosrc
        for srpm in srpm1, srpm2:
            data =  koji.get_header_fields(srpm, ['arch'], src_arch=True)
            self.assertEqual(data['arch'], 'nosrc')



if __name__ == '__main__':
    unittest.main()
