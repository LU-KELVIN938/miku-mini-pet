@echo off
cd /d "%~dp0"
echo Open http://127.0.0.1:8765/ to compare the animations.
py -3.13 tools\serve_preview.py
