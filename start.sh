#!/usr/bin/env bash
set -e

# ==============================================================================
# Agent Firewall - 1-Click Installation & Startup Script
# ==============================================================================

# Formatting utilities
BOLD="\033[1m"
GREEN="\033[32m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}=============================================${RESET}"
echo -e "${BLUE}${BOLD}   🛡️  Agent Firewall Launcher 🛡️          ${RESET}"
echo -e "${BLUE}${BOLD}=============================================${RESET}"
echo ""

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "📄 Creating default .env from .env.example..."
    cp .env.example .env
fi

echo "How would you like to run the Agent Firewall?"
echo -e "  ${GREEN}[1] Docker Compose (Recommended - 1 Click)${RESET}"
echo "  [2] Natively on Host (Requires local PostgreSQL)"
echo ""
read -p "Select option [1/2]: " RUN_MODE

if [ "$RUN_MODE" = "1" ] || [ -z "$RUN_MODE" ]; then
    echo -e "\n${GREEN}🚀 Starting via Docker Compose...${RESET}"
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker or run natively.${RESET}"
        exit 1
    fi
    docker compose up --build -d
    
    echo -e "\n${BOLD}=============================================${RESET}"
    echo -e "${GREEN}✅ All services started successfully!${RESET}"
    echo -e "👉 Dashboard:  ${BLUE}http://localhost:3000${RESET}"
    echo -e "👉 API:        ${BLUE}http://localhost:8001${RESET}"
    echo -e "👉 Gateway:    ${BLUE}http://localhost:8000${RESET}"
    echo -e "\nRun 'docker compose logs -f' to view live logs."
    echo -e "${BOLD}=============================================${RESET}"
    exit 0
fi

if [ "$RUN_MODE" = "2" ]; then
    echo -e "\n${BLUE}🚀 Starting Natively...${RESET}"
    
    # 1. Check for Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed. Please install Node.js 20+ first.${RESET}"
        exit 1
    fi

    # 2. Check for Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10+ first.${RESET}"
        exit 1
    fi

    # 3. Check for uv
    if ! command -v uv &> /dev/null; then
        echo -e "📦 Installing Astral 'uv' for lightning-fast Python envs..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
    fi

    # Graceful exit handler
    cleanup() {
        echo -e "\n${RED}🛑 Shutting down all native services...${RESET}"
        kill $(jobs -p) 2>/dev/null
        wait
        exit
    }
    trap cleanup SIGINT SIGTERM

    echo -e "\n${BOLD}[1/3] Starting Web Dashboard (Next.js)...${RESET}"
    cd apps/web
    npm install
    npm run dev &
    cd ../..

    echo -e "\n${BOLD}[2/3] Starting API Control Plane (FastAPI)...${RESET}"
    cd apps/api
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    
    # Run Alembic migrations natively
    alembic upgrade head || echo -e "${RED}⚠️ Alembic migration failed. Is PostgreSQL running on localhost:5432?${RESET}"
    
    uvicorn main:app --port 8001 &
    deactivate
    cd ../..

    echo -e "\n${BOLD}[3/3] Starting Gateway Proxy (FastAPI)...${RESET}"
    cd apps/gateway
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    uvicorn main:app --port 8000 &
    deactivate
    cd ../..

    echo -e "\n${BOLD}=============================================${RESET}"
    echo -e "${GREEN}✅ All services are booting up in the background!${RESET}"
    echo -e "👉 Dashboard:      ${BLUE}http://localhost:3000${RESET}"
    echo -e "👉 API:            ${BLUE}http://localhost:8001${RESET}"
    echo -e "👉 Gateway:        ${BLUE}http://localhost:8000${RESET}"
    echo -e "\n${RED}Press Ctrl+C to terminate all services.${RESET}"
    echo -e "${BOLD}=============================================${RESET}"
    
    # Wait indefinitely until SIGINT is received
    wait
fi
