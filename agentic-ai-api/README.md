pip freeze > requirements.txt
python -m venv .venv
.venv\Scripts\activate

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
