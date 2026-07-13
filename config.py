import os
from pathlib import Path


class Config:
    DATABASE = str(Path(__file__).resolve().parent / "residents.db")
    SECRET_KEY = "residence_records_secret"