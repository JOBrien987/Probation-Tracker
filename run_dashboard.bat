@echo off
title Probation Caseload Risk Dashboard

echo Installing/checking required Python packages...
python -m pip install -r requirements.txt

echo.
echo Starting dashboard...
python -m streamlit run app.py

pause
