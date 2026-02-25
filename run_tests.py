# run_tests.py
"""
Run all project tests using pytest.
Sets environment variable TESTING=True before running.
Stops on first failure and shows short traceback for clarity.
"""

import pytest
import os

if __name__ == '__main__':
    # Set test environment
    os.environ['TESTING'] = 'True'
    # Run pytest with verbose output, short traceback, stop after first failure
    pytest.main(['-v', '--tb=short', '-x'])