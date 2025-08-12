from srmtimetable.utils import pickle_login
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    filename = pickle_login(username, password)
    print(f"Session saved to {filename}")
    # Run this script to save the session to a pickle file.
    # Make sure to set the USERNAME and PASSWORD environment variables in a .env file before running this script.
