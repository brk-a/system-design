#!/usr/bin/env python3

# Adaptee 1: Old Database
class OldDatabase:
    def fetch_data_from_old_system(self):
        return "Data from Old Database"

# Adaptee 2: New API
class NewAPI:
    def get_data_from_new_api(self):
        return "Data from New API"

# Target: Unified data fetching interface
class DataFetcher:
    def fetch_data(self):
        pass

# Adapter 1: Adapter for OldDatabase
class OldDatabaseAdapter(DataFetcher):
    def __init__(self, old_db: OldDatabase):
        self.old_db = old_db
    
    def fetch_data(self):
        print("Fetching data using Old Database adapter...")
        return self.old_db.fetch_data_from_old_system()

# Adapter 2: Adapter for NewAPI
class NewAPIAdapter(DataFetcher):
    def __init__(self, new_api: NewAPI):
        self.new_api = new_api
    
    def fetch_data(self):
        print("Fetching data using New API adapter...")
        return self.new_api.get_data_from_new_api()

# Client code
def client_code(data_fetcher: DataFetcher):
    data = data_fetcher.fetch_data()
    print(f"Fetched Data: {data}")

# Using the adapters
old_db = OldDatabase()
new_api = NewAPI()

old_db_adapter = OldDatabaseAdapter(old_db)
new_api_adapter = NewAPIAdapter(new_api)

client_code(old_db_adapter)
client_code(new_api_adapter)