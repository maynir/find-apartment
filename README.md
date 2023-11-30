# Find Apartment

## Description
Find relevant facebook post about apartments based on keywords.

## Installation
1. Clone the repository: `git clone git@github.com:maynir/find-apartment.git`
2. Navigate to the project directory: `cd find-apartment`
3. Install dependencies: `pip3 install -r requirements.txt`

### Configuration

Create a configuration file `config.py` and fill in the necessary settings:

```python
my_email = "your_facebook_email@gmail.com"
password = "your_facebook_password"
mongo_connection = "mongodb://localhost:27017/"
```

### MongoDB Setup
Before running the application, make sure you have a local MongoDB service running. If not, follow these steps:

1. Download and install MongoDB for your operating system: `brew install mongodb-community`
2. Start the MongoDB service: `brew services start mongodb-community`
3. Connect to MongoDb: `mongosh`

Now, your local MongoDB service is up and running.

## Usage
To use My Awesome Project, follow these steps:

```bash
python3 scrape_with_sel.py
```