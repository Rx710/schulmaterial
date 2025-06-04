from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Associationstabelle für n:m zwischen Material und Tag
table_material_tag = db.Table(
    'material_tag',
    db.Column('MaterialID', db.Integer, db.ForeignKey('material.MaterialID'), primary_key=True),
    db.Column('TagID', db.Integer, db.ForeignKey('tag.TagID'), primary_key=True)
)

class Rolle(db.Model):
    __tablename__ = 'rolle'
    RollenID = db.Column(db.Integer, primary_key=True)
    Bezeichnung = db.Column(db.String(50), nullable=False)

class Benutzer(db.Model):
    __tablename__ = 'benutzer'
    BenutzerID = db.Column(db.Integer, primary_key=True)
    Vorname = db.Column(db.String(100), nullable=False)
    Nachname = db.Column(db.String(100), nullable=False)
    EMail = db.Column(db.String(255), unique=True)
    PasswortHash = db.Column(db.String(255))
    RollenID = db.Column(db.Integer, db.ForeignKey('rolle.RollenID'))

    rolle = db.relationship('Rolle', backref='benutzer')
    kommentare = db.relationship('Kommentar', backref='autor', lazy=True)
    favoriten = db.relationship('Favorit', backref='benutzer', lazy=True)

class Thema(db.Model):
    __tablename__ = 'thema'
    ThemaID = db.Column(db.Integer, primary_key=True)
    Bezeichnung = db.Column(db.String(100), nullable=False)
    Beschreibung = db.Column(db.Text)

    materialien = db.relationship('Material', backref='thema', lazy=True)

class Material(db.Model):
    __tablename__ = 'material'
    MaterialID = db.Column(db.Integer, primary_key=True)
    Erstelldatum = db.Column(db.DateTime, default=datetime.utcnow)
    Änderungsdatum = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    Dateiname = db.Column(db.String(255), nullable=False)
    Dateityp = db.Column(db.String(50), nullable=False)
    AutorenID = db.Column(db.Integer, db.ForeignKey('benutzer.BenutzerID'))
    ThemenID = db.Column(db.Integer, db.ForeignKey('thema.ThemaID'))
    SpeicherModus = db.Column(db.Enum('BLOB', 'PFAD'), nullable=False)
    Binaerdaten = db.Column(db.LargeBinary)
    Dateipfad = db.Column(db.String(500))

    autor = db.relationship('Benutzer', backref='materialien')
    versionen = db.relationship('Version', backref='material', lazy=True)
    kommentare = db.relationship('Kommentar', backref='material', lazy=True)
    tags = db.relationship('Tag', secondary=table_material_tag, backref='materialien')
    favoriten = db.relationship('Favorit', backref='material', lazy=True)

class Version(db.Model):
    __tablename__ = 'version'
    VersionID = db.Column(db.Integer, primary_key=True)
    MaterialID = db.Column(db.Integer, db.ForeignKey('material.MaterialID'))
    VersionNummer = db.Column(db.String(10), nullable=False)
    Änderungsdatum = db.Column(db.DateTime, default=datetime.utcnow)
    Beschreibung = db.Column(db.String(500))
    SpeicherModus = db.Column(db.Enum('BLOB', 'PFAD'), nullable=False)
    Binaerdaten = db.Column(db.LargeBinary)
    Dateipfad = db.Column(db.String(500))

class Tag(db.Model):
    __tablename__ = 'tag'
    TagID = db.Column(db.Integer, primary_key=True)
    Bezeichnung = db.Column(db.String(100), unique=True, nullable=False)

class Kommentar(db.Model):
    __tablename__ = 'kommentar'
    KommentarID = db.Column(db.Integer, primary_key=True)
    MaterialID = db.Column(db.Integer, db.ForeignKey('material.MaterialID'))
    AutorID = db.Column(db.Integer, db.ForeignKey('benutzer.BenutzerID'))
    Erstelldatum = db.Column(db.DateTime, default=datetime.utcnow)
    LetzteAenderung = db.Column(
        'LetzteÄnderung',
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    Kommentartext = db.Column(db.Text, nullable=False)

class Favorit(db.Model):
    __tablename__ = 'favorit'
    FavoritID = db.Column(db.Integer, primary_key=True)
    BenutzerID = db.Column(db.Integer, db.ForeignKey('benutzer.BenutzerID'))
    MaterialID = db.Column(db.Integer, db.ForeignKey('material.MaterialID'))
    HinzugefuegtDatum = db.Column(
        'HinzugefügtDatum',
        db.DateTime,
        default=datetime.utcnow,
    )
