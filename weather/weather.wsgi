import os
import sys

sys.path.append('/vagrant')
sys.path.append('/vagrant/weather')
#sys.path.append('/vagrant/weather/weatherapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
