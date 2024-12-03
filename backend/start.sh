#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Starting Backend Services...${NC}"

docker-compose down

docker-compose build --no-cache
docker-compose up -d

sleep 10

echo -e "${YELLOW}Running migrations...${NC}"
docker-compose exec -T backend python manage.py makemigrations
docker-compose exec -T backend python manage.py migrate

echo -e "${YELLOW}Creating superuser...${NC}"
docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

echo -e "${YELLOW}Creating initial cryptocurrencies...${NC}"
docker-compose exec -T backend python manage.py shell << EOF
from api.models import CryptoCurrency
currencies = [
    {"name": "Curve DAO", "symbol": "CRV", "price": 0},
    {"name": "Curve USD", "symbol": "crvUSD", "price": 0},
    {"name": "Stake DAO CRV", "symbol": "sdCRV", "price": 0},
    {"name": "Ethereum", "symbol": "ETH", "price": 0},
    {"name": "Stable CRV", "symbol": "sCRV", "price": 0}
]
for currency in currencies:
    CryptoCurrency.objects.get_or_create(**currency)
EOF

echo -e "${GREEN}Backend setup complete!${NC}"
echo -e "${BLUE}You can access:${NC}"
echo "- GraphQL: http://localhost:8000/graphql"
echo "- Admin: http://localhost:8000/admin (admin/admin)"