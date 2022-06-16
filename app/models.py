import django
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.



class TodoAdd(models.Model):
    user  = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task = models.CharField(max_length=150)
    datetime = models.DateTimeField(auto_now=True)
    
    
class TokenAdd(models.Model):
    token = models.CharField(max_length=150)
    user =  models.ForeignKey(get_user_model(), on_delete=models.CASCADE)        