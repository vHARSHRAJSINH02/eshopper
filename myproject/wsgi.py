"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os   # for import os module
 
from django.core.wsgi import get_wsgi_application  # importing function from wsgi module  django.core = packege , wsgi=module,  get_wsgi_application = function
from dj_static import Cling

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = Cling(get_wsgi_application())