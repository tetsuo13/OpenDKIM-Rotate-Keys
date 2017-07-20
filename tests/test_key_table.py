import os
import shutil
import tempfile
import unittest

from odkim_rotate.key_table import KeyTable

class KeyTableTests(unittest.TestCase):
    def setUp(self):
        self.key_table_file = tempfile.mkstemp()[1]

    def tearDown(self):
        os.unlink(self.key_table_file)

    def write_key_file_contents(self, keyfile):
        with open(self.key_table_file, 'w') as f:
            for short_name in keyfile:
                line = '{}  {}:{}:{}\n'.format(
                    short_name,
                    keyfile[short_name][KeyTable.DOMAIN],
                    keyfile[short_name][KeyTable.SELECTOR],
                    keyfile[short_name][KeyTable.PRIVATE_KEY])
                f.write(line)

    def test_simple_load(self):
        key_dir = tempfile.mkdtemp()

        try:
            keyfile = {
                'example': {
                    KeyTable.DOMAIN: 'example.com',
                    KeyTable.SELECTOR: '20170101',
                    KeyTable.PRIVATE_KEY: key_dir + '/example.private'
                },
                'replacehandsaw': {
                    KeyTable.DOMAIN: 'replacehandsaw.test',
                    KeyTable.SELECTOR: '20170201',
                    KeyTable.PRIVATE_KEY: key_dir + '/replacehandsaw.private'
                }}

            self.write_key_file_contents(keyfile)
            keytable = KeyTable(self.key_table_file)

            self.assertEqual(2, len(keytable))

            for short_name, values in keytable:
                self.assertTrue(short_name in keyfile)
                self.assertEqual(keyfile[short_name][KeyTable.DOMAIN],
                                 values[KeyTable.DOMAIN])
                self.assertEqual(keyfile[short_name][KeyTable.SELECTOR],
                                 values[KeyTable.SELECTOR])
                self.assertEqual(keyfile[short_name][KeyTable.PRIVATE_KEY],
                                 values[KeyTable.PRIVATE_KEY])
        finally:
            shutil.rmtree(key_dir)

    def test_sorted_by_short_name(self):
        key_dir = tempfile.mkdtemp()

        try:
            keyfile = {
                'foo': {
                    KeyTable.DOMAIN: 'foo.test',
                    KeyTable.SELECTOR: '20170101',
                    KeyTable.PRIVATE_KEY: key_dir + '/foo.test'
                },
                'bar': {
                    KeyTable.DOMAIN: 'bar.test',
                    KeyTable.SELECTOR: '20170201',
                    KeyTable.PRIVATE_KEY: key_dir + '/bar.test'
                },
                'apple': {
                    KeyTable.DOMAIN: 'apple.test',
                    KeyTable.SELECTOR: '20170201',
                    KeyTable.PRIVATE_KEY: key_dir + '/apple.test'
                }}

            self.write_key_file_contents(keyfile)
            keytable = KeyTable(self.key_table_file)

            self.assertEqual(3, len(keytable))

            self.assertEqual(keyfile['apple'][KeyTable.DOMAIN],
                             keytable[0][KeyTable.DOMAIN])
            self.assertEqual(keyfile['bar'][KeyTable.DOMAIN],
                             keytable[1][KeyTable.DOMAIN])
            self.assertEqual(keyfile['foo'][KeyTable.DOMAIN],
                             keytable[2][KeyTable.DOMAIN])
        finally:
            shutil.rmtree(key_dir)

    def test_short_name_padding(self):
        key_dir = tempfile.mkdtemp()

        try:
            keyfile = {
                'unitedmonkey': {
                    KeyTable.DOMAIN: 'foo.test',
                    KeyTable.SELECTOR: '20170101',
                    KeyTable.PRIVATE_KEY: key_dir + '/foo.test'
                },
                'bar': {
                    KeyTable.DOMAIN: 'bar.test',
                    KeyTable.SELECTOR: '20170201',
                    KeyTable.PRIVATE_KEY: key_dir + '/bar.test'
                },
                'apple': {
                    KeyTable.DOMAIN: 'apple.test',
                    KeyTable.SELECTOR: '20170201',
                    KeyTable.PRIVATE_KEY: key_dir + '/apple.test'
                }}

            self.write_key_file_contents(keyfile)
            keytable = KeyTable(self.key_table_file)

            self.assertEqual(3, len(keytable))

            keytable.save_changes()

            selector_format = '{:' + \
                              str(len('unitedmonkey') + KeyTable.SELECTOR_PADDING) + \
                              '}{}'

            with open(self.key_table_file) as f:
                lines = f.read().splitlines()

            for selector, i in [('apple', 0), ('bar', 1), ('unitedmonkey', 2)]:
                beginningtext = selector_format.format(selector, keyfile[selector][KeyTable.DOMAIN])
                self.assertTrue(lines[i].startswith(beginningtext))
        finally:
            shutil.rmtree(key_dir)

    def test_update_selector(self):
        key_dir = tempfile.mkdtemp()

        try:
            keyfile = {
                'orangeauto': {
                    KeyTable.DOMAIN: 'orangeauto.test',
                    KeyTable.SELECTOR: '20170101',
                    KeyTable.PRIVATE_KEY: key_dir + '/orangeauto.test'
                }}

            self.write_key_file_contents(keyfile)
            keytable = KeyTable(self.key_table_file)

            self.assertEqual(1, len(keytable))
            self.assertEqual('20170101', keytable.entries['orangeauto'][KeyTable.SELECTOR])

            keytable.update_selector('orangeauto', '20170201')
            self.assertEqual('20170201', keytable.entries['orangeauto'][KeyTable.SELECTOR])
        finally:
            shutil.rmtree(key_dir)

