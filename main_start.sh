#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Starting Full Stack Setup...${NC}"

echo -e "${YELLOW}Starting Backend...${NC}"
cd backend
./start.sh

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backend started successfully!${NC}"
else
    echo -e "${RED}Backend failed to start${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting Frontend...${NC}"
cd ../frontend
./start.sh

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Frontend started successfully!${NC}"
else
    echo -e "${RED}Frontend failed to start${NC}"
    exit 1
fi

echo -e "\n${GREEN}=======================${NC}"
echo -e "${GREEN}🎉 All services are up! ${NC}"
echo -e "${GREEN}=======================${NC}\n"

echo -e "${BLUE}You can access:${NC}"
echo "1. Backend:"
echo "   - GraphQL: http://localhost:8000/graphql"
echo "   - Admin: http://localhost:8000/admin (admin/admin)"
echo "2. Frontend:"
echo "   - Web App: http://localhost:3000"
echo -e "\n${YELLOW}To view logs:${NC}"
echo "Backend: cd backend && docker-compose logs -f"
echo "Frontend: cd frontend && docker-compose logs -f"