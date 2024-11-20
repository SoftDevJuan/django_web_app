import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_roles.settings')

<<<<<<< HEAD
application = get_asgi_application()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django_roles import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_roles.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
=======
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
>>>>>>> 2d4a58f3d641d72a6b7fa650545078bde8c15cbc
        )
    ),
})

<<<<<<< HEAD
=======


>>>>>>> 2d4a58f3d641d72a6b7fa650545078bde8c15cbc
