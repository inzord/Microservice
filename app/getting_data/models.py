from django.db import models


class Url(models.Model):
    data = models.DateTimeField()

    def __str__(self):
        return self.data
