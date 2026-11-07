import os
from pathlib import Path
from dotenv import *

load_dotenv()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
BASE_DIR = Path(__file__).resolve().parent.parent
MAX_UPLOAD_REQUEST_BYTES = int(os.getenv("MAX_UPLOAD_REQUEST_BYTES", 1024 ** 3))
