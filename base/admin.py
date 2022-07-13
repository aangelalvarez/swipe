from django.contrib import admin
from .models import Room, Message

admin.site.register(Room) # So that we can work with rooms in the admin panel
admin.site.register(Message)