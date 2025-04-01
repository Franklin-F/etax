bind = '0.0.0.0:8088'
workers = 1
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
accesslog = '/var/log/gunicorn/etax.access.log'
errorlog = '/var/log/gunicorn/etax.error.log'
