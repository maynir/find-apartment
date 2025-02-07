#!/bin/bash

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null
then
    echo "pipenv is not installed. Installing pipenv..."
    pip3 install --user pipenv
fi

# Create and activate the virtual environment
echo "Setting up the project..."
pipenv install

echo "Setup complete! Use 'pipenv shell' to enter the environment."
