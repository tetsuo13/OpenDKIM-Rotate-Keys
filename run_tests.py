#!/usr/bin/env python

import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    runner = unittest.runner.TextTestRunner()
    runner.run(tests)

