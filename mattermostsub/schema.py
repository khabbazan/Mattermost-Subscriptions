import graphene
import graphql_jwt

from apps.account.gql.mutations import UserCreate
from apps.account.gql.mutations import UserGetToken
from apps.account.gql.queries import UserList
from apps.chat.gql.mutations import ChannelCreate
from apps.chat.gql.mutations import TextMessageSend
from apps.chat.gql.queries import ChannelList
from apps.chat.gql.queries import GetMessageList
from apps.chat.gql.subscriptions import OnNewChatMessage


class Query(UserList, ChannelList, GetMessageList):
    pass


class Mutation(graphene.ObjectType):
    user_create = UserCreate.Field()
    user_get_token = UserGetToken.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    text_message_send = TextMessageSend.Field()
    channel_create = ChannelCreate.Field()


class Subscription(graphene.ObjectType):
    on_new_chat_message = OnNewChatMessage.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
