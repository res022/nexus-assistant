# -*- coding: utf-8 -*-
# Test script to find available Gemini models
import google.generativeai as genai
from config import Config
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print(f"API Key configured: {bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here')}")

if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here':
    genai.configure(api_key=Config.GEMINI_API_KEY)

    print("\n=== Available Models ===")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"[OK] {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\n=== Testing Models ===")
    test_models = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-pro'
    ]

    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"[OK] {model_name} - WORKS")
        except Exception as e:
            print(f"[FAIL] {model_name} - {str(e)[:100]}")
else:
    print("ERROR: Gemini API key not configured!")
