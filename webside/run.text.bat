@echo off
start cmd
start http://127.0.0.1:8000/
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "& 'c:/Users/sudha/OneDrive/Documents/projects/BAT/webside/test1/venv/Scripts/Activate.ps1'; cd C:\Users\sudha\OneDrive\Documents\projects\BAT\webside\test1\webside\; python manage.py runserver"
