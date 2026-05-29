"""
ASGI config for stageflow project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stageflow.settings')

application = get_asgi_application()
