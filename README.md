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
4. Activate the virtual environment: `pipenv shell`
    * To deactivate run: `exit`

### Configuration

Create a configuration file `config.py` and fill in the necessary settings:

```python
my_email = "your_facebook_email@gmail.com"
password = "your_facebook_password"
mongo_connection = "mongodb://localhost:27017/"
```

### MongoDB Setup
Before running the application, make sure you have a local MongoDB service running. If not, follow these steps:

1. **Install MongoDB**
   ```sh
   brew tap mongodb/brew
   brew install mongodb-community@7.0  # Install the latest stable version
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

Now, your local MongoDB service is up and running.

## Usage
To use my project, follow these steps:

```sh
python3 scrape_with_sel.py
```