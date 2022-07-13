from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True) 
    # This value can be null and the form blank
    updated = models.DateTimeField(auto_now=True)
    # auto_now saves date and time whenever this class gets updated
    created = models.DateTimeField(auto_now_add= True)
    # auto_now_add saves the date and time once an instance of this class is created

    class Meta:
        ordering = ['-updated', '-created'] # sort rooms
        
    def __str__(self):
        return self.name
        

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # CASCADE if a room is deleted all its children (messages) are deleted as well
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:35]