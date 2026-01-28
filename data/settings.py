from dotenv import load_dotenv
from pathlib import Path


# -------- Directories --------

ROOT_DIR = Path(__file__).resolve().parent.parent

GUI_DIR = ROOT_DIR / "gui"

SRC_DIR = ROOT_DIR / "src"

API_DIR = ROOT_DIR / "api"

SERVICES_DIR = ROOT_DIR / "services"

DATA_DIR = ROOT_DIR / "data"

SCRIPTS_DIR = ROOT_DIR / "scripts"

TESTS_DIR = ROOT_DIR / "tests"


# -------- Files --------

ENV_FILE = ROOT_DIR / ".env"


# -------- Functions --------

def env_load():
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE)


# -------- Load .env variables --------

env_load()
