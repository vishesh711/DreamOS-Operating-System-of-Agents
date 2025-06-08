#!/bin/bash

# DreamOS Vercel Deployment Script
# This script helps to deploy DreamOS to Vercel

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}DreamOS Vercel Deployment Script${NC}"
echo "====================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}Vercel CLI not found. Installing...${NC}"
    npm install -g vercel
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Vercel CLI. Please install it manually:${NC}"
        echo "npm install -g vercel"
        exit 1
    fi
else
    echo -e "${GREEN}Vercel CLI is already installed.${NC}"
fi

echo ""
echo -e "${YELLOW}Please ensure you have the following before continuing:${NC}"
echo "1. A Vercel account"
echo "2. Required environment variables ready (check VERCEL_DEPLOYMENT.md)"
echo ""

read -p "Do you want to continue with deployment? (y/n): " continue_deploy

if [[ $continue_deploy != "y" && $continue_deploy != "Y" ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}Logging in to Vercel...${NC}"
vercel login

echo ""
echo -e "${GREEN}Starting deployment...${NC}"
echo "This will deploy DreamOS to Vercel. Follow the prompts to complete setup."
echo ""

# Deploy to Vercel
vercel

echo ""
echo -e "${GREEN}Deployment process completed.${NC}"
echo "Check the Vercel dashboard for deployment status and logs."
echo "If you encounter any issues, refer to VERCEL_DEPLOYMENT.md for troubleshooting." 