"""
HabitPulse Configuration
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'habitpulse-dev-key-2025'
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'habitpulse.db')
    DEBUG = True
