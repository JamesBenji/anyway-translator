from django.db import models

# Create your models here.
'''
    1. db model (RoomMember) | Store username, uid and channel name
    2. on join, create RoomMember in from django.db import models
    3. on handleUserJoin event, query the db for room member by uid (since its what each user has access to)
    4. on leave, delete RoomMember
'''

class RoomMember(models.Model):
    name = models.CharField(max_length=200)
    uid = models.CharField(max_length=200)
    room_name = models.CharField(max_length=200)
    
    def __str___(self):
        return self.name