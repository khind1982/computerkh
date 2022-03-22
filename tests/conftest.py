import os
import sys

# sys.path.append(
#         os.path.abspath(os.path.join(os.path.dirname(__file__), '../bsc')))
# sys.path.append(
#         os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_configure(config):
    sys._tests_running = True

def pytest_unconfigure(config):
    del sys._tests_running
