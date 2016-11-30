#! /bin/bash

cd /Users/dz8t/MTData
source venv/bin/activate
pip install -r requirements.txt
cd MTData/
python export.py
