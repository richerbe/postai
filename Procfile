web: gunicorn --bind 0.0.0.0:8000 web.server:app
worker: python -m streamlit run ../app.py --server.port 8501
