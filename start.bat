@echo off
title RepeatMe
cd /d "%~dp0"
python server.py || py server.py
if errorlevel 1 pause
