"""Beispieldaten für eine lokale Testumgebung."""

from werkzeug.security import generate_password_hash
from models import db, Rolle, Benutzer, Thema, Material, Tag, Kommentar, Favorit


def seed_test_data():
    """Fügt Beispieldaten ein, falls die Tabellen noch leer sind."""
    # Rollen
    if Rolle.query.count() == 0:
        lehrkraft = Rolle(Bezeichnung='Lehrkraft')
        auszubildender = Rolle(Bezeichnung='Auszubildender')
        db.session.add_all([lehrkraft, auszubildender])
        db.session.commit()
    else:
        lehrkraft = Rolle.query.filter_by(Bezeichnung='Lehrkraft').first()
        auszubildender = Rolle.query.filter_by(Bezeichnung='Auszubildender').first()

    # Benutzer
    if Benutzer.query.count() == 0:
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
    else:
        user1 = Benutzer.query.filter_by(EMail='anna.lehrer@example.com').first()
        user2 = Benutzer.query.filter_by(EMail='ben.auszug@example.com').first()

    # Themen
    if Thema.query.count() == 0:
        thema1 = Thema(Bezeichnung='Informatik', Beschreibung='Informatik-Themen')
        thema2 = Thema(Bezeichnung='Mathematik', Beschreibung='Mathematik-Themen')
        db.session.add_all([thema1, thema2])
        db.session.commit()
    else:
        thema1 = Thema.query.filter_by(Bezeichnung='Informatik').first()
        thema2 = Thema.query.filter_by(Bezeichnung='Mathematik').first()

    # Tags
    if Tag.query.count() == 0:
        tag1 = Tag(Bezeichnung='Einführung')
        tag2 = Tag(Bezeichnung='Fortgeschritten')
        db.session.add_all([tag1, tag2])
        db.session.commit()
    else:
        tag1 = Tag.query.filter_by(Bezeichnung='Einführung').first()
        tag2 = Tag.query.filter_by(Bezeichnung='Fortgeschritten').first()

    # Material
    if Material.query.count() == 0:
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
            Binaerdaten=b'Fake DOCX-Inhalt'
        )
        material2.tags.extend([tag1, tag2])

        db.session.add_all([material1, material2])
        db.session.commit()
    else:
        material1 = Material.query.filter_by(Dateiname='grundlagen.pdf').first()
        material2 = Material.query.filter_by(Dateiname='mathe_uebung.docx').first()

    # Kommentar
    if Kommentar.query.count() == 0 and material1 and user2:
        kommentar1 = Kommentar(
            MaterialID=material1.MaterialID,
            AutorID=user2.BenutzerID,
            Kommentartext='Sehr hilfreiches Material!'
        )
        db.session.add(kommentar1)
        db.session.commit()

    # Favorit
    if Favorit.query.count() == 0 and material1 and user2:
        favorit1 = Favorit(
            BenutzerID=user2.BenutzerID,
            MaterialID=material1.MaterialID
        )
        db.session.add(favorit1)
        db.session.commit()
