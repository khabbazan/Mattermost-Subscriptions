import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from mattermostsub.consumers import MyGraphqlWsConsumer
from mattermostsub.middlewares import JWTwsAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mattermostsub.settings")

application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": JWTwsAuthMiddleware(AuthMiddlewareStack(URLRouter([path("ws/graphql/", MyGraphqlWsConsumer.as_asgi())])))}
)
