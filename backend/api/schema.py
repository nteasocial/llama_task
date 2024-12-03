import graphene
from django.utils import timezone
from .models import CryptoCurrency


class CryptoCurrencyType(graphene.ObjectType):
    name = graphene.String()
    symbol = graphene.String()
    defillama_id = graphene.String()
    price = graphene.Float()
    last_updated = graphene.DateTime()


class Query(graphene.ObjectType):
    all_cryptocurrencies = graphene.List(CryptoCurrencyType)

    def resolve_all_cryptocurrencies(self, info):
        return CryptoCurrency.objects.all()


class CreateCryptoCurrency(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        symbol = graphene.String(required=True)
        defillama_id = graphene.String(required=True)

    cryptocurrency = graphene.Field(CryptoCurrencyType)

    def mutate(self, info, name, symbol, defillama_id):
        crypto = CryptoCurrency.objects.create(
            name=name, symbol=symbol, defillama_id=defillama_id, price=0, last_updated=timezone.now()
        )
        return CreateCryptoCurrency(cryptocurrency=crypto)


class Mutation(graphene.ObjectType):
    create_cryptocurrency = CreateCryptoCurrency.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
