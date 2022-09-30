from django.db import models

# Create your models here.
class Todolist(models.Model):
    todolist = models.CharField(max_length=100, blank=True, null=True)
