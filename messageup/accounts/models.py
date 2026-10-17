from django.db import models

# Create your models here.
class Account(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True )
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username

class password_reset(models.Model):
    email = models.EmailField()
    reset_token = models.CharField(max_length=255 ,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email