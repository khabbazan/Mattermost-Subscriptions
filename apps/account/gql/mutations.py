import graphene
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.forms.models import model_to_dict
from graphql_jwt.shortcuts import create_refresh_token
from graphql_jwt.shortcuts import get_token

from helpers import http_code
from helpers.generic_types import ResponseBase
from helpers.generic_types import ResponseUnion
from helpers.generic_types import ResponseWithToken
from helpers.mattermostproxydriver.admin import MattermostAdminProxy


class UserCreate(graphene.Mutation):
    """
    UserCreate Mutation
    This mutation is used to create a new user. It involves creating a user in the Django system
    and additionally in an external system (Mattermost) through an admin proxy.
    """

    class Arguments:
        username = graphene.Argument(graphene.String, required=True, description="Username for the new user account.")
        password = graphene.Argument(graphene.String, required=True, description="Password for the new user account.")
        email = graphene.Argument(graphene.String, required=True, description="Email address for the new user account.")

    Output = ResponseBase

    def mutate(self, info, username, password, email):
        """
        Mutate function for the UserCreate Mutation.
        Creates a new user in the database and Mattermost, returns a success response upon completion.
        """
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            matter_admin = MattermostAdminProxy()
            creation_status = matter_admin.create_user(user_data={"username": user.username, "email": user.email, "password": user.password[:30]})
            add_to_team_status = matter_admin.add_user_to_team(user_identifier=user.username)
            if not (creation_status and add_to_team_status):
                raise Exception("mattermost operation failed.")

        return ResponseBase(status=http_code.HTTP_200_OK, status_code=http_code.HTTP_200_OK_CODE, message="User created successfully!")


class UserGetToken(graphene.Mutation):
    """
    UserGetToken Mutation
    This mutation is used to retrieve an authentication token for an existing user in the system.
    It validates the user credentials and returns a JWT token and refresh token upon successful authentication.
    """

    class Arguments:
        username = graphene.Argument(graphene.String, required=True, description="Username of the user for authentication.")
        password = graphene.Argument(graphene.String, required=True, description="Password of the user for authentication.")

    Output = ResponseUnion

    def mutate(self, info, username, password):
        """
        Mutate function for the UserGetToken Mutation.
        Authenticates a user and provides an authentication token and a refresh token if successful.
        """
        user = authenticate(username=username, password=password)

        if user:
            return ResponseWithToken(
                status=http_code.HTTP_200_OK,
                status_code=http_code.HTTP_200_OK_CODE,
                message="Login Successfully!",
                token=get_token(user),
                refresh_token=create_refresh_token(user),
                metadata={k: v for k, v in model_to_dict(user).items() if k in ["id", "username", "email"]},
            )
        else:
            return ResponseBase(
                status=http_code.HTTP_404_NOT_FOUND,
                status_code=http_code.HTTP_404_NOT_FOUND_CODE,
                message="Login Failed!",
            )
