"""
GraphQL Schema with Apollo Federation support
"""
import strawberry
from strawberry.federation import Schema
from .resolvers import Query, Mutation


# Create GraphQL schema with Federation support
schema = Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True
)

