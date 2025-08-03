from srmtimetable.utils import pickle_login
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    filename = pickle_login(username, password)
    print(f"Session saved to {filename}")
