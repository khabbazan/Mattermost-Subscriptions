import graphene
from graphene.types import generic


class ResponseBase(graphene.ObjectType):
    """
    Represents a basic response object.

    Attributes:
        status (graphene.String): The status of the response.
        status_code (graphene.Int): The HTTP status code of the response.
        message (graphene.String): A message associated with the response.
        metadata (generic.GenericScalar): Additional metadata associated with the response.
    """

    status = graphene.String(description="The status of the response.")
    status_code = graphene.Int(description="The HTTP status code of the response.")
    message = graphene.String(description="A message associated with the response.")
    metadata = generic.GenericScalar(description="Additional metadata associated with the response.")


class ResponseWithToken(graphene.ObjectType):
    """
    Represents a response object with authentication tokens.

    Attributes:
        status (graphene.String): The status of the response.
        status_code (graphene.Int): The HTTP status code of the response.
        message (graphene.String): A message associated with the response.
        token (graphene.String): An authentication token.
        refresh_token (graphene.String): A refresh token.
        metadata (generic.GenericScalar): Additional metadata associated with the response.
    """

    status = graphene.String(description="The status of the response.")
    status_code = graphene.Int(description="The HTTP status code of the response.")
    message = graphene.String(description="A message associated with the response.")
    token = graphene.String(description="An authentication token.")
    refresh_token = graphene.String(description="A refresh token.")
    metadata = generic.GenericScalar(description="Additional metadata associated with the response.")


class ResponseUnion(graphene.Union):
    """
    Represents a union of response types for dynamic outputs in mutations.

    Types:
        - ResponseWithToken: A response with authentication tokens.
        - ResponseBase: A basic response.

    Usage:
        Use this union for dynamic outputs in mutations.
    """

    class Meta:
        types = (
            ResponseWithToken,
            ResponseBase,
        )


class PageType(graphene.InputObjectType):
    """
    Represents an input object for specifying pagination parameters.

    Attributes:
        page_size (graphene.Int): The number of items per page.
        page_number (graphene.Int): The page number.
    """

    page_size = graphene.Int(description="The number of items per page.")
    page_number = graphene.Int(description="The page number.")

