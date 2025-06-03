FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Anforderungen installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Port und Startbefehl
CMD ["flask", "run", "--host=0.0.0.0"]