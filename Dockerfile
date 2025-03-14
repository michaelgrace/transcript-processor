FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory and ensure permissions
RUN mkdir -p data && chmod 777 data

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py"]