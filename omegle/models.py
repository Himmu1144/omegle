from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class WaitingArea(models.Model):

    users = models.ManyToManyField(User, verbose_name=("waiting-users"), blank=True)

    def add_user(self, user):
        """
        return true if user is added to the users list
        """
        is_user_added = False
        if not user in self.users.all():
            self.users.add(user)
            self.save()
            is_user_added = True
        elif user in self.users.all():
            is_user_added = True
        return is_user_added 


    def remove_user(self, user):
        """
        return true if user is removed from the users list
        """
        is_user_removed = False
        if user in self.users.all():
            self.users.remove(user)
            self.save()
            is_user_removed = True
        return is_user_removed 

    def __str__(self):
        return 'waiting list'

class GroupConnect(models.Model):
    user1 = models.ForeignKey(User, verbose_name="User_1", related_name='user_1' , on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, verbose_name="User_2", related_name='user_2' , on_delete=models.CASCADE)

    def group_name(self,user1,user2):
        return f'{self.user1.id}{self.user2.id}'

    def __str__(self):
        return f'{self.user1.id}{self.user2.id}'
    