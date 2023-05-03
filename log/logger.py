# -*- coding: utf-8 -*-

import logging
import os.path

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_path = os.getcwd() + '/logs/'
log_name = log_path + 'ui' + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

