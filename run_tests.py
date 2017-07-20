#!/usr/bin/env python

import os
import sys
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    runner = unittest.runner.TextTestRunner()

    if not runner.run(tests).wasSuccessful():
        sys.exit(os.EX_SOFTWARE)

