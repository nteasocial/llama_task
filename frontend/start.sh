#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Frontend Services...${NC}"

docker-compose down

docker-compose build --no-cache
docker-compose up -d

echo -e "${GREEN}Frontend setup complete!${NC}"
echo -e "${BLUE}You can access the application at:${NC}"
echo "http://localhost:3000"