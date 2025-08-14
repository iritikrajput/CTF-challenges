# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ctf-lab-super-secret-key-2024'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///ctf_lab.db'
    
    # CTF specific settings
    CTF_NAME = "SQL Injection CTF Lab"
    CTF_VERSION = "2.0"
    MAX_ATTEMPTS_PER_IP = 100
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
