import graphene
from api.schema import Query as api_query
from api.schema import Mutation as api_mutation


class Query(api_query, graphene.ObjectType):
    pass


class Mutation(api_mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
