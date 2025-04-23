# Find Apartment

## Description
Find relevant facebook post about apartments based on keywords.

## Prerequisites
- Python 3 installed (`python3 --version`)
- `pipenv` installed (`pip3 install --user pipenv`)

## Installation
1. Clone the repository: `git clone git@github.com:maynir/find-apartment.git`
2. Navigate to the project directory: `cd find-apartment`
3. Run the setup script: `./setup.sh`
   * This script will:
     - Install pipenv if not already installed
     - Install MongoDB (for macOS users) if not already installed
     - Start the MongoDB service
     - Verify MongoDB is running correctly
     - Install all project dependencies using pipenv
     - Create the required MongoDB database and collection
4. Activate the virtual environment: `pipenv shell`
   * To deactivate run: `exit`

### Configuration

Create a configuration file `src/etc/config.py` and fill in the necessary settings:

```python
MY_EMAIL = "your_facebook_email@gmail.com"
PASSWORD = "your_facebook_password"
MONGO_CONNECTION = "mongodb://localhost:27017/"
TELEGRAM_CHAT_ID = ""
TELEGRAM_BOT_TOKEN = ""
OPENAI_API_KEY = "your_openai_api_key"
BUDGET_THRESHOLD = 7000 # set your budget threshold here
```

### MongoDB Setup
The setup script automatically handles MongoDB installation and configuration for macOS users. It will:

1. Install MongoDB Community Edition 7.0 if not already installed
2. Start the MongoDB service
3. Verify the MongoDB connection
4. Create the required database (`apartmentsdb`) and collection (`apartments`)

If you need to manually manage MongoDB:

1. **Install MongoDB**
   ```sh
   brew tap mongodb/brew
   brew install mongodb-community@7.0
   ```
2. **Start MongoDB**
   ```sh
   brew services start mongodb-community@7.0
   ```
3. **Verify MongoDB is running**
   ```sh
   ps aux | grep mongod
   ```
4. **Connect to MongoDB**
   ```sh
   mongosh
   ```

## Usage
To use my project, follow these steps:

```sh
python3 src/main.py
```

To format the code, run:

```sh
pipenv run black .
```

To sort imports, run:

```sh
pipenv run isort .
```
