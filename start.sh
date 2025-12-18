#!/bin/bash
# Uruchomienie Social Media Analyzer (GUI)

cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app.py
