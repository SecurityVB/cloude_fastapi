import os
from pathlib import Path
from dotenv import *

load_dotenv()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
BASE_DIR = Path(__file__).resolve().parent.parent