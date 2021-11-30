import os
from dotenv import load


load()

API_KEY = os.getenv("API_KEY")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SHOP_URL = os.getenv("SHOP_URL")
API_VERSION = os.getenv("API_VERSION")
