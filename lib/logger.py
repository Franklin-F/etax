import logging

# create logger with 'etax'
logger = logging.getLogger('etax')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh1 = logging.FileHandler('app.log', encoding='utf-8')
fh1.setLevel(logging.DEBUG)
# create file handler which logs error messages
fh2 = logging.FileHandler('err.log', encoding='utf-8')
fh2.setLevel(logging.ERROR)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh1.setFormatter(formatter)
fh2.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh1)
logger.addHandler(fh2)
logger.addHandler(ch)
