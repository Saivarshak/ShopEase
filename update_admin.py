import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopease.settings')
django.setup()

from django.contrib.auth.models import User

username = 'saivarshak14@gmail.com'
email = 'saivarshak14@gmail.com'
password = '1111'

user, created = User.objects.get_or_create(username=username)
user.email = email
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.save()

if created:
    print(f"Superuser {username} created successfully.")
else:
    print(f"Superuser {username} updated successfully.")
