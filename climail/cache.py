import sqlite3
from pathlib import Path
from platformdirs import user_config_dir

PRJ_DIR = Path(user_config_dir("CLIMAIL"))
CACHE_FILE = PRJ_DIR / "CLIMAIL.db"

def init_db():
    conn = sqlite3.connect(CACHE_FILE)