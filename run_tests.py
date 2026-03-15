# run_tests.py
import pytest
import os

if __name__ == '__main__':
    # Set test environment
    os.environ['TESTING'] = 'True'
    # Run pytest with detailed output and stop after first failure
    pytest.main(['-v', '--tb=short', '-x'])