# -*- coding: utf-8 -*-
"""
Configuration file for the Georgian Law Database Application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-2.0-flash'  # Latest stable model

    # Law file settings
    LAWS_DIRECTORY = 'laws'
    METADATA_SEPARATOR = '---METADATA---'

    # AI Assistant settings
    MAX_LAWS_TO_SEND = 7  # Maximum number of laws to send to Gemini (increased for better coverage)
    MAX_CONVERSATION_HISTORY = 10  # Keep last 10 messages

    # Language settings
    DEFAULT_LANGUAGE = 'ka'  # Georgian
    SUPPORTED_LANGUAGES = ['ka', 'en']

    # Admin Panel settings
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')  # Change in .env!

    @staticmethod
    def validate():
        """Validate configuration"""
        if not Config.GEMINI_API_KEY:
            print("[WARNING] GEMINI_API_KEY not set. AI features will not work.")
            print("[INFO] Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        return True
