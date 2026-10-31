# BhashaSetu AI

## Overview
BhashaSetu AI is a workplace language assistance application designed to help Hindi and Gujarati speakers communicate more clearly.

## Features
- Hindi to Gujarati translation
- Gujarati to Hindi translation
- Workplace instruction clarity checking
- Smart workplace translation
- Hindi and Gujarati text-to-speech
- Speech-to-text integration using Gnani AI
- Automated tests using pytest

## Technology Stack
- Python
- Gnani AI Speech-to-Text and Text-to-Speech
- Groq API for translation
- Pytest

## Requirements
- Python
- Valid Gnani AI and Groq API keys
- Internet connection for API requests

## Setup
1. Open a terminal in the project directory.
2. Install dependencies using: pip install -r requirements.txt
3. Create a .env file in the project root.
4. Add the required API keys using the variable names expected by config.py.
5. Run the application using: python app.py

## Testing
Run automated tests using: python -m pytest -q

The current test suite contains 18 tests, which passed in the development environment.

## Safety and Limitations
- Never publish API keys or secrets.
- Translation quality depends on the underlying AI service.
- Verify important workplace instructions before acting on them.

## Project Demo & Documentation

- **LinkedIn Demo:** [Watch BhashaSetu AI Demo](https://lnkd.in/p/dcEfM9-A)
- **Project Documentation:** See `docs/` folder.