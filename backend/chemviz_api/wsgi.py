"""
WSGI config for CHEM•VIZ API project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemviz_api.settings')

if os.environ.get('VERCEL'):
    import django
    from pathlib import Path
    Path('/tmp/media').mkdir(parents=True, exist_ok=True)
    django.setup()
    from django.core.management import call_command
    call_command('migrate', '--no-input', verbosity=0)

application = get_wsgi_application()

# Vercel Python runtime expects `app`
app = application
