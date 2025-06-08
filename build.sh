#!/bin/bash

# DreamOS Vercel Build Script
# This script runs during Vercel build process

echo "Starting DreamOS build process for Vercel..."

# Create necessary directories
mkdir -p dreamos/memory
mkdir -p dreamos/plugins
mkdir -p dreamos/memory/visualizations
mkdir -p dreamos/memory/databases
mkdir -p dreamos/memory/metrics
mkdir -p dreamos/logs

echo "Directory structure created successfully."

# Set proper permissions
chmod +x deploy_to_vercel.sh

echo "Build completed successfully." 