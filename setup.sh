#!/bin/bash

# Exit script on error
set -e

echo "🔄 Setting up the project..."

# Ensure Homebrew is installed (for macOS users)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo "⚠️ Homebrew not found. Please install it from https://brew.sh/"
        exit 1
    fi
fi

# Install pipenv if not installed
if ! command -v pipenv &> /dev/null; then
    echo "📦 pipenv not found. Installing pipenv..."
    pip3 install --user pipenv
fi

# Install MongoDB (for macOS users)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🛠 Checking and installing MongoDB..."
    if ! command -v mongosh &> /dev/null; then
        brew tap mongodb/brew
        brew install mongodb-community@7.0
    fi

    echo "🚀 Starting MongoDB service..."
    brew services start mongodb-community@7.0
fi

# Verify MongoDB is running
echo "🛠 Checking if MongoDB is running..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️ MongoDB is not running. Please start it manually: mongod --fork --logpath /var/log/mongodb.log --dbpath /data/db"
    exit 1
fi

# Verify MongoDB connection
if command -v mongosh &> /dev/null; then
    echo "✅ MongoDB installation verified. Connecting..."
    mongosh --eval "db.runCommand({ connectionStatus: 1 })"
else
    echo "❌ MongoDB shell (mongosh) not found. Ensure MongoDB is properly installed."
    exit 1
fi

# Install project dependencies
echo "📦 Installing dependencies using pipenv..."
pipenv install

# Create MongoDB database and collection
echo "🛠 Setting up MongoDB database and collection..."
mongosh <<EOF
use apartmentsdb
db.createCollection("apartments")
print("✅ MongoDB setup complete: Database 'apartmentsdb' and collection 'apartments' created.")

use yad2db
db.createCollection("apartments")
print("✅ MongoDB setup complete: Database 'yad2db' and collection 'apartments' created.")
EOF

echo "🎉 Setup completed successfully!"
echo "ℹ️ To activate the virtual environment, run: pipenv shell"
