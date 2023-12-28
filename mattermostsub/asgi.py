
import os

from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from mattermostsub.consumers import MyGraphqlWsConsumer
from mattermostsub.middlewares import JWTwsAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mattermostsub.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTwsAuthMiddleware(
        AuthMiddlewareStack(URLRouter([
                path("ws/graphql/", MyGraphqlWsConsumer.as_asgi())
            ])
        )
    )
})
