#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'counselling_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_reports():
    User = get_user_model()
    client = Client()
    
    print('Testing reports page with simple template...')
    
    admin = User.objects.get(username='admin')
    client.force_login(admin)
    response = client.get('/reports/')
    print(f'Reports page status: {response.status_code}')
    
    if response.status_code == 200:
        print('SUCCESS: Reports page working with simple template!')
    else:
        print(f'Still getting error: {response.status_code}')
        if hasattr(response, 'content'):
            content = response.content.decode()[:500]
            print(f'Error content: {content}')

if __name__ == '__main__':
    test_reports()
