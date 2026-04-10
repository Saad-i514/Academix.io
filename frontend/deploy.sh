#!/bin/bash
# Vercel Deployment Script for Academix.io Frontend

echo "Starting Vercel deployment..."

# Set environment variable
export NEXT_PUBLIC_API_URL=https://academixio-production.up.railway.app

# Deploy to Vercel
vercel --prod --yes

echo "Deployment complete!"
