import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType


class UserQueryType(DjangoObjectType):
    """
    DjangoObjectType for the User model.
    This class creates a GraphQL type for the Django User model, including selected fields.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff")  # Specifying the fields to include in the GraphQL type


class UserListType(graphene.ObjectType):
    """
    GraphQL ObjectType for representing a list of users.
    This type includes the data of users, the total number of pages for pagination,
    and the count of total users available.
    """

    data = graphene.List(UserQueryType, description="List of users.")
    page_count = graphene.Int(description="Total number of pages available for the paginated list of users.")
    count = graphene.Int(description="Total count of users.")
