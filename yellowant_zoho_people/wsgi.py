"""
WSGI config for yellowant_todoapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yellowant_zoho_people.settings")

DEV_ENV = os.environ.get("ENV")
if DEV_ENV == "heroku":
    os.system('echo "from django.contrib.auth.models import User; User.objects.create_superuser(\'admin\', \'admin@example.com\', \'pass\')" | python manage.py shell')

application = get_wsgi_application()
