-- Rolle-Tabelle und Standardrollen
CREATE TABLE IF NOT EXISTS rolle (
  RollenID INT AUTO_INCREMENT PRIMARY KEY,
  Bezeichnung VARCHAR(50) NOT NULL
);

-- Thema-Tabelle und Beispielthemen
CREATE TABLE IF NOT EXISTS thema (
  ThemaID INT AUTO_INCREMENT PRIMARY KEY,
  Bezeichnung VARCHAR(100) NOT NULL,
  Beschreibung TEXT
);


-- Benutzer-Tabelle und Beispielbenutzer
CREATE TABLE IF NOT EXISTS benutzer (
  BenutzerID INT AUTO_INCREMENT PRIMARY KEY,
  Vorname VARCHAR(100) NOT NULL,
  Nachname VARCHAR(100) NOT NULL,
  EMail VARCHAR(255) UNIQUE,
  PasswortHash VARCHAR(255),
  RollenID INT,
  FOREIGN KEY (RollenID) REFERENCES rolle(RollenID)
);

-- Material-Tabelle
CREATE TABLE IF NOT EXISTS material (
  MaterialID INT AUTO_INCREMENT PRIMARY KEY,
  Erstelldatum DATETIME DEFAULT CURRENT_TIMESTAMP,
  Änderungsdatum DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  Dateiname VARCHAR(255) NOT NULL,
  Dateityp VARCHAR(50) NOT NULL,
  AutorenID INT,
  ThemenID INT,
  SpeicherModus ENUM('BLOB','PFAD') NOT NULL,
  Binaerdaten LONGBLOB,
  Dateipfad VARCHAR(500),
  FOREIGN KEY (AutorenID) REFERENCES benutzer(BenutzerID),
  FOREIGN KEY (ThemenID) REFERENCES thema(ThemaID)
);

-- Version-Tabelle
CREATE TABLE IF NOT EXISTS version (
  VersionID INT AUTO_INCREMENT PRIMARY KEY,
  MaterialID INT,
  VersionNummer VARCHAR(10) NOT NULL,
  Änderungsdatum DATETIME DEFAULT CURRENT_TIMESTAMP,
  Beschreibung VARCHAR(500),
  SpeicherModus ENUM('BLOB','PFAD') NOT NULL,
  Binaerdaten LONGBLOB,
  Dateipfad VARCHAR(500),
  FOREIGN KEY (MaterialID) REFERENCES material(MaterialID)
);

-- Tag-Tabelle
CREATE TABLE IF NOT EXISTS tag (
  TagID INT AUTO_INCREMENT PRIMARY KEY,
  Bezeichnung VARCHAR(100) UNIQUE NOT NULL
);

-- Junction-Tabelle material_tag (n:m zwischen Material und Tag)
CREATE TABLE IF NOT EXISTS material_tag (
  MaterialID INT,
  TagID INT,
  PRIMARY KEY (MaterialID, TagID),
  FOREIGN KEY (MaterialID) REFERENCES material(MaterialID),
  FOREIGN KEY (TagID) REFERENCES tag(TagID)
);

-- Kommentar-Tabelle
CREATE TABLE IF NOT EXISTS kommentar (
  KommentarID INT AUTO_INCREMENT PRIMARY KEY,
  MaterialID INT,
  AutorID INT,
  Erstelldatum DATETIME DEFAULT CURRENT_TIMESTAMP,
  LetzteÄnderung DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  Kommentartext TEXT NOT NULL,
  FOREIGN KEY (MaterialID) REFERENCES material(MaterialID),
  FOREIGN KEY (AutorID) REFERENCES benutzer(BenutzerID)
);

-- Favorit-Tabelle
CREATE TABLE IF NOT EXISTS favorit (
  FavoritID INT AUTO_INCREMENT PRIMARY KEY,
  BenutzerID INT,
  MaterialID INT,
  HinzugefügtDatum DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (BenutzerID) REFERENCES benutzer(BenutzerID),
  FOREIGN KEY (MaterialID) REFERENCES material(MaterialID)
);
