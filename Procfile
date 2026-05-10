web: cd web && gunicorn --workers 4 --timeout 120 server:app
worker: python -m streamlit run ../app.py --server.port 8501
