import graphene
from graphene_django import DjangoObjectType
from .models import CryptoCurrency


class CryptoCurrencyType(DjangoObjectType):
    class Meta:
        model = CryptoCurrency
        fields = ('id', 'name', 'symbol', 'price', 'last_updated')


class Query(graphene.ObjectType):
    all_cryptocurrencies = graphene.List(CryptoCurrencyType)
    cryptocurrency = graphene.Field(
        CryptoCurrencyType, symbol=graphene.String())

    def resolve_all_cryptocurrencies(self, info):
        return CryptoCurrency.objects.all()

    def resolve_cryptocurrency(self, info, symbol):
        try:
            return CryptoCurrency.objects.get(symbol=symbol)
        except CryptoCurrency.DoesNotExist:
            return None


class CreateCryptoCurrency(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        symbol = graphene.String(required=True)
        # Changed from Float to Decimal
        price = graphene.Decimal(required=True)

    cryptocurrency = graphene.Field(CryptoCurrencyType)

    def mutate(self, info, name, symbol, price):
        cryptocurrency = CryptoCurrency.objects.create(
            name=name,
            symbol=symbol,
            price=price
        )
        return CreateCryptoCurrency(cryptocurrency=cryptocurrency)


class Mutation(graphene.ObjectType):
    create_cryptocurrency = CreateCryptoCurrency.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
