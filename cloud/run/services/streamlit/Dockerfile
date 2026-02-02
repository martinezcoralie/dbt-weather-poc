FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY cloud/run/services/streamlit/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/bi-streamlit /app/apps/bi-streamlit

EXPOSE 8080

CMD ["streamlit", "run", "apps/bi-streamlit/app.py", "--server.address=0.0.0.0", "--server.port=8080"]
