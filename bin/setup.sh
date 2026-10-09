#!/usr/bin/env bash



##NOTE this must be run from a GitBash terminal!!
## bash bin/setup.sh

set -e

echo "== Agricore Setup =="

cd backend

#create our .venv if it doesn't already exist
if [ ! -d ".venv" ]; then
    echo "Creating Virtual Environment..."
    python -m venv .venv
else
    echo "Virtual Environment already exists."
fi

source .venv/Scripts/activate
pip install -r requirements.txt

#create .env file if it doesn't exist already
if [ ! -f ".env" ]; then
    echo "No .env found - copying from .env.example."
    echo "Fill in real values in backend/.env before running the app."
    cp .env.example .env
else
    echo ".env file already exists."
fi

#Frontend setup
cd ../frontend
if [ -d "node_modules" ]; then
    echo "Frontend node_modules already exists. Verifying..."
fi

npm install

echo "Setup complete"