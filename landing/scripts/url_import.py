#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_landing.settings')
django.setup()

from landing.management.commands.parse_page import Command  # Или скопируйте _methods

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python url_import.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    cmd = Command()
    cmd.handle(url=url)