from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    is_vendedor = models.BooleanField(default=False)
    cep = models.CharField(max_length=9, blank=True)