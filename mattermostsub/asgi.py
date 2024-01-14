import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

django_asgi_app = get_asgi_application()

from mattermostsub.consumers import MyGraphqlWsConsumer
from mattermostsub.middlewares import JWTwsAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mattermostsub.settings")

application = ProtocolTypeRouter(
    {"http": django_asgi_app, "websocket": JWTwsAuthMiddleware(AuthMiddlewareStack(URLRouter([path("ws/graphql/", MyGraphqlWsConsumer.as_asgi())])))}
)
