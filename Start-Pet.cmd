@echo off
cd /d "%~dp0"
py -3.13 desktop\launch.py
if errorlevel 1 pause
