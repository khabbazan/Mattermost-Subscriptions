from helpers.channels_graphql_ws import graphql_ws_consumer
from mattermostsub.schema import schema


class MyGraphqlWsConsumer(graphql_ws_consumer.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""

    schema = schema

    # send keepalive message every 42 seconds.
    # send_keepalive_every = 42

    async def on_connect(self, payload):
        """New client connection handler."""
        print("New client connected!")
