"""
Vercel serverless entry point for Progspresso
This file is the entry point for Vercel's Python runtime
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and expose the Flask app
# Vercel expects the WSGI app to be named 'app'
from app import app as application

app = application
