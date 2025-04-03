from django.db import models


from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.db import models, transaction
from django.contrib.auth.hashers import make_password, check_password



class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'books'


    def __str__(self):
        return self.title

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    @classmethod
    def create_user(cls, username, password, email, first_name=None, role='user'):
        with transaction.atomic():
            user = cls(
                username=username,
                email=email,
                first_name=first_name,
                role=role
            )
            user.password = make_password(password)
            user.save()
            return user


