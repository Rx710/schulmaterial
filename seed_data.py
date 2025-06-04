from app import create_app
from models import db, Rolle, Benutzer, Thema, Material, Tag, Kommentar, Favorit
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Rollen anlegen
    lehrkraft = Rolle(Bezeichnung='Lehrkraft')
    auszubildender = Rolle(Bezeichnung='Auszubildender')
    db.session.add_all([lehrkraft, auszubildender])
    db.session.commit()

    # Benutzer anlegen
    user1 = Benutzer(
        Vorname='Anna',
        Nachname='Lehrer',
        EMail='anna.lehrer@example.com',
        PasswortHash=generate_password_hash('lehrerpass'),
        RollenID=lehrkraft.RollenID,
    )
    user2 = Benutzer(
        Vorname='Ben',
        Nachname='Auszubildender',
        EMail='ben.auszug@example.com',
        PasswortHash=generate_password_hash('azubipass'),
        RollenID=auszubildender.RollenID,
    )
    db.session.add_all([user1, user2])
    db.session.commit()

    # Themen anlegen
    thema1 = Thema(Bezeichnung='Informatik', Beschreibung='Informatik-Themen')
    thema2 = Thema(Bezeichnung='Mathematik', Beschreibung='Mathematik-Themen')
    db.session.add_all([thema1, thema2])
    db.session.commit()

    # Tags anlegen
    tag1 = Tag(Bezeichnung='Einführung')
    tag2 = Tag(Bezeichnung='Fortgeschritten')
    db.session.add_all([tag1, tag2])
    db.session.commit()

    # Material anlegen (kleine Datei als Beispiel, Binaerdaten = Dummy)
    material1 = Material(
        Dateiname='grundlagen.pdf',
        Dateityp='pdf',
        AutorenID=user1.BenutzerID,
        ThemenID=thema1.ThemaID,
        SpeicherModus='BLOB',
        Binaerdaten=b'Testinhalte',
    )
    material1.tags.append(tag1)

    material2 = Material(
        Dateiname='mathe_uebung.docx',
        Dateityp='docx',
        AutorenID=user1.BenutzerID,
        ThemenID=thema2.ThemaID,
        SpeicherModus='BLOB',
        Binaerdaten=b'''Fake DOCX-Inhalt'''
    )
    material2.tags.extend([tag1, tag2])

    db.session.add_all([material1, material2])
    db.session.commit()

    # Kommentar anlegen
    kommentar1 = Kommentar(
        MaterialID=material1.MaterialID,
        AutorID=user2.BenutzerID,
        Kommentartext='Sehr hilfreiches Material!'
    )
    db.session.add(kommentar1)
    db.session.commit()

    # Favorit anlegen
    favorit1 = Favorit(
        BenutzerID=user2.BenutzerID,
        MaterialID=material1.MaterialID
    )
    db.session.add(favorit1)
    db.session.commit()

    print('Testdaten wurden erfolgreich angelegt.')