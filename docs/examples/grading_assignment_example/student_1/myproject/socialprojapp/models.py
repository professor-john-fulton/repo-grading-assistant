from django.db import models



# Create your models here.

#class Contact(models.Model):
   # first_name = models.CharField(max_length=100)
   # last_name = models.CharField(max_length=100)
   # email = models.EmailField(max_length=150)
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=300)

    def __str__(self):
        return self.title