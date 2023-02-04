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
        
        while True:
            group_name = await fetch_group(user1)
            if group_name:
                break
        if group_name:
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
            print('User1 Added to the group')

            await self.send_json({
                'join' : group_name,
                'user1_id' : str(user1.id),
                'user1' : 'user1',
                'spinner' : 'You are now Connected with a Stranger'
            })


    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        print("ChatConsumer: receive_json")
        command = content.get("command", None)
        try:
            if command == "send":
                print('we made it till here')
                print(content['user1_id'])
                print(content['message'])
                await self.send_room(content["group_name"], content['user1_id'], content["message"])
            elif command == "get_room_chat_messages":
                pass
            elif command == "get_user_info":
                pass
        except ClientError as e:
            await self.handle_client_error(e)
            print('command stopped here')

    async def send_room(self, group_name, user1_id, message):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        print("PublicChatConsumer: send_room")

        # if str(self.id) != str(user1_id):
        #     raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
        
        # Get the group and send to the group about it

        
        print('The group name is - ',group_name)

        await self.channel_layer.group_send(
            str(group_name),
            {
                "type": "chat.message",
                "username": "id : " + str(user1_id),
                "message": message,
            }
        )

        print('msg sent to the group')

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        print("PublicChatConsumer: chat_message from user #" + str(event["username"]))
        await self.send_json(
            {
                "msg_type": 0,
                "username": event["username"],
                "message": event["message"],
            },
        )



    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        user1 = await get_user(self.id)
        group_name = await fetch_group(user1)
        group_name = str(group_name)

        await self.channel_layer.group_send(
            group_name,
            {
                "type": "leave.message",
                "spinner": 'Chat Disconnected',
                "id" : user1.id,
            }
        )

        await self.channel_layer.group_discard(
			group_name,
			self.channel_name,
		)
        print(f'Group - {group_name} Discarded')
        await delete_user(self.id)
        print('User deleted')

      
    async def leave_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": 1,
                "spinner": event["spinner"],
                'id' : event['id']
            },
        )


    # async def join_room(self, room_id):
    #     """
    #     Called by receive_json when someone sent a join command.
    #     """
    #     # The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
    #     print("ChatConsumer: join_room: " + str(room_id))



    # async def leave_room(self, room_id):
    #     """
    #     Called by receive_json when someone sent a leave command.
    #     """
    #     # The logged-in user is in our scope thanks to the authentication ASGI middleware
    #     print("ChatConsumer: leave_room")


    async def handle_client_error(self, e):
        """
        Called when a ClientError is raised.
        Sends error data to UI.
        """
        errorData = {}
        errorData['error'] = e.code
        if e.message:
            errorData['message'] = e.message
            await self.send_json(errorData)
        return

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
    return str(group_name)

@database_sync_to_async
def fetch_group(user):
    try:
        group_name = GroupConnect.objects.get(Q(user1=user)|Q(user2=user))
        group_name = str(group_name)
    except:
        group_name = None
    return group_name

@database_sync_to_async
def fetch_group_id(id):
    try:
        group_name = GroupConnect.objects.get(pk=id)
        group_name = str(group_name)
    except:
        group_name = None
    return group_name

class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    def __init__(self, code, message):
        super().__init__(code)
        self.code = code
        if message:
        	self.message = message