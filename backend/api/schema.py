import graphene
from django.utils import timezone
from .models import CryptoCurrency


class CryptoCurrencyType(graphene.ObjectType):
    name = graphene.String()
    symbol = graphene.String()
    price = graphene.Float()
    last_updated = graphene.DateTime()


class Query(graphene.ObjectType):
    all_cryptocurrencies = graphene.List(CryptoCurrencyType)
    cryptocurrency = graphene.Field(
        CryptoCurrencyType,
        symbol=graphene.String(required=True)
    )

    def resolve_all_cryptocurrencies(self, info):
        return CryptoCurrency.objects.all()

    def resolve_cryptocurrency(self, info, symbol):
        return CryptoCurrency.objects.filter(symbol=symbol).first()


class CreateCryptoCurrency(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        symbol = graphene.String(required=True)

    cryptocurrency = graphene.Field(CryptoCurrencyType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name, symbol):
        try:
            crypto = CryptoCurrency.objects.create(
                name=name,
                symbol=symbol,
                price=0,
                last_updated=timezone.now()
            )
            return CreateCryptoCurrency(
                cryptocurrency=crypto,
                success=True,
                message="Cryptocurrency created successfully"
            )
        except Exception as e:
            return CreateCryptoCurrency(
                cryptocurrency=None,
                success=False,
                message=str(e)
            )


class UpdateCryptocurrencyPrice(graphene.Mutation):
    class Arguments:
        symbol = graphene.String(required=True)
        price = graphene.Float(required=True)

    cryptocurrency = graphene.Field(CryptoCurrencyType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, symbol, price):
        try:
            crypto = CryptoCurrency.objects.get(symbol=symbol)
            crypto.price = price
            crypto.last_updated = timezone.now()
            crypto.save()
            return UpdateCryptocurrencyPrice(
                cryptocurrency=crypto,
                success=True,
                message="Price updated successfully"
            )
        except CryptoCurrency.DoesNotExist:
            return UpdateCryptocurrencyPrice(
                cryptocurrency=None,
                success=False,
                message=f"Cryptocurrency with symbol {symbol} not found"
            )


class Mutation(graphene.ObjectType):
    create_cryptocurrency = CreateCryptoCurrency.Field()
    update_cryptocurrency_price = UpdateCryptocurrencyPrice.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
