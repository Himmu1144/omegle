from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from omegle.utils import generateOTP
from omegle.models import WaitingArea , GroupConnect
from django.db.models import Q
import random


class ChatConsumer(AsyncJsonWebsocketConsumer):


    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        print("ChatConsumer: connect: ")

        await self.accept()

        user1_id = await create_user()
        user1 = await get_user(user1_id)
        self.id = user1_id
        print(f'user - {user1} is connected')
        print(f'Adding user - {user1} to waiting List')
        added = await adding_user_to_waiting(user1)

        fetched_user1 = await fetch_user(user1)
        if fetched_user1:
            print('User 1 fetched')
        if fetched_user1:
            remove_user1 = await removing_user_from_waiting(fetched_user1)
            print('removed_user1_from_WL')

        user2 = await random_user()
        if user2:
            fetched_user2 = await fetch_user(user2)
            if fetched_user2:
                remove_user2 = await removing_user_from_waiting(fetched_user2)
                print('user2_fetched')
            if fetched_user1 and fetched_user2:
                group_name = await create_group(fetched_user1, fetched_user2)
                print('The Group is created')
        else:
            added = await adding_user_to_waiting(user1)
            print('User2 was not present in the WL so added User1 again')
        
        group_name = await fetch_group(user1)
        if group_name:
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
            print('User1 Added to the group')

        


    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        print("ChatConsumer: receive_json")
        command = content.get("command", None)
        try:
            if command == "join":
                pass
            elif command == "leave":
                pass
            elif command == "send":
                pass
            elif command == "get_room_chat_messages":
                pass
            elif command == "get_user_info":
                pass
        except Exception as e:
            pass


    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        user1 = get_user(self.id)
        group_name = await fetch_group(user1)
        await self.channel_layer.group_discard(
			group_name,
			self.channel_name,
		)
        print(f'Group - {group_name} Discarded')
        await delete_user(self.id)
        print('User deleted')
      


    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
        print("ChatConsumer: join_room: " + str(room_id))



    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        print("ChatConsumer: leave_room")



    async def send_room(self, room_id, message):
        """
        Called by receive_json when someone sends a message to a room.
        """
        print("ChatConsumer: send_room")

@database_sync_to_async
def create_user():
    id = generateOTP()
    username = str(id)
    password = id
    user = User.objects.create_user(pk=id,username=username, password=password)
    user.is_active = False
    user.save()
    return id
    

@database_sync_to_async
def delete_user(id):
    user = User.objects.get(id=id)
    user.delete()
    return None

@database_sync_to_async
def get_user(id):
    user = User.objects.get(pk=id)
    return user

@database_sync_to_async
def adding_user_to_waiting(user):
    try:
        waiting_list = WaitingArea.objects.get(pk=1)
    except:
        waiting_list = WaitingArea.objects.create(pk=1)
    added = False
    if waiting_list:
        is_added = waiting_list.add_user(user)
        added = is_added
    return added

@database_sync_to_async
def removing_user_from_waiting(user):
    try:
        waiting_list = WaitingArea.objects.get(pk=1)
    except:
        waiting_list = WaitingArea.objects.create(pk=1)
    removed = False
    if waiting_list:
        is_removed = waiting_list.remove_user(user)
        removed = is_removed
    return removed

@database_sync_to_async
def fetch_user(user):
    try:
        group_name = GroupConnect.objects.get(Q(user1=user)|Q(user2=user))
    except:
        group_name = None
    if group_name:
        user = None
    else:
        user = User.objects.get(pk=user.id)
    return user

@database_sync_to_async
def random_user():
    try:
        waiting_list = WaitingArea.objects.get(pk=1)
        users = waiting_list.users.all()
        if users:
            random_user = random.choice(users)
        else:
            random_user = None
    except WaitingArea.DoesNotExist:
        return None
    return random_user

@database_sync_to_async
def create_group(user1,user2):
    group_name = GroupConnect.objects.create(user1=user1,user2=user2)
    return group_name

@database_sync_to_async
def fetch_group(user):
    try:
        group_name = GroupConnect.objects.get(Q(user1=user)|Q(user2=user))
        group_name = str(group_name)
    except:
        group_name = None
    return group_name
