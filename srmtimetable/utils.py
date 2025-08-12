import base64
import pickle
import base64
import os
from io import BytesIO
import time
from .academia import login


def pickle_login(username, password):
    """
    Login to Academia and save the session to a pickle file.

    Args:
        username (str): The username for Academia.
        password (str): The password for Academia.
    """
    session = login(username, password)
    filename = f"{username}_{int(time.time())}.pickle"
    with open(f"creds/{filename}", "wb") as f:
        pickle.dump(session, f)
    return filename


def load_pickle_login(filename):
    """
    Load the session from the pickle file.

    Returns:
        requests.Session: The session object loaded from the pickle file.
    """
    with open(f"creds/{filename}", "rb") as f:
        session = pickle.load(f)
    return session


def save_to_file(data, filename):
    """
    Save data to a file.

    Args:
        data (any): The data to save.
        filename (str): The name of the file to save the data to.
    """
    os.makedirs("data", exist_ok=True)
    with open(f"data/{filename}", "w") as f:
        f.write(data)


def fig_to_base64(fig):
    """
    Convert a matplotlib figure to a base64 encoded string.
    Args:
        fig (matplotlib.figure.Figure): The figure to convert."""
    buf = BytesIO()
    fig.patch.set_alpha(0.0)
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def save_base64_image(base64_string, path):
    """
    Save a base64 encoded image to a file.
    Args:
        base64_string (str): The base64 encoded image string.
        path (str): The file path where the image will be saved.
    """
    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_string))
