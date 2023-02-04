from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from omegle_main.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from omegle.consumers import ChatConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
				
				path('chat/', ChatConsumer.as_asgi()),
				
				]
				
			)
		)
	),
})