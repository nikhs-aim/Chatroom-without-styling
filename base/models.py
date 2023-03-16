from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Topic(models.Model):      # topic can have many rooms
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):      # room can have only one topic
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  # it cannot be blank
    # participants =
    # changes every time the data is saved
    updates = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)  # initial time stamp


    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updates = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)  # initial time stamp

    def __str__(self):
        return self.body[0:50]
