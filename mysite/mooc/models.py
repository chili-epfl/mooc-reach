from django.db import models
from django.utils import timezone

class Search(models.Model):
    keyword = models.CharField(max_length = 140);
    derivative = models.BooleanField(default= False);

    def __str__(self):
        return self.keyword


