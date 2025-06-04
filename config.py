"""Konfigurationswerte für die Flask-Anwendung."""

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Basiskonfiguration für Flask und SQLAlchemy."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://lernuser:lernpass@localhost:3306/lernmaterialdb'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Speicherordner für größere Dateien (>1 MB)
    # Ordner auf dem Hostsystem, in dem große Dateien abgelegt werden
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    # Maximale erlaubte Dateigröße (z.B. 16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
