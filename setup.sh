#!/bin/bash

# Step 1: Setup .venv with python3 if it doesn't exist
if [ ! -d ".venv" ]
then
    python3 -m venv .venv
    echo "Virtual environment (.venv) is created."
else
    echo "Virtual environment (.venv) already exists."
fi

# Step 2: Source it
source .venv/bin/activate
echo "Virtual environment (.venv) is activated."

# Step 3: Install dependencies from requirement.txt
if [ -f "requirements.txt" ]
then
    pip install -r requirements.txt
    echo "Dependencies from requirements.txt are installed."
else
    echo "requirements.txt not found. No dependencies to install."
fi