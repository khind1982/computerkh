# -*- mode: python -*-

# Add logging to transformation toolchain apps.

import datetime
import logging
import logging.config
import logging.handlers
import os

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
confdir = os.path.join(APP_ROOT, 'etc')

def _setup_logdir():
    logdir = os.path.join(os.path.expanduser('~'), 'transformationlogs')
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

def get_logger():
    _setup_logdir()
    os.datetime = datetime
    logconfig = os.path.join(confdir, 'transformationLogging.conf')
    logging.config.fileConfig(logconfig)
    del os.datetime
    return logging.getLogger('tr')
