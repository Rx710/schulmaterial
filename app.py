import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from io import BytesIO
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError

from config import Config
from models import db, Rolle, Benutzer, Thema, Material, Version, Tag, Kommentar, Favorit
from testdata import seed_test_data

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'supersecretkey'  # Für Flash-Messages (kann man später via Umgebungsvariable ersetzen)

    # SQLAlchemy initialisieren
    db.init_app(app)

    # Sicherstellen, dass Upload-Ordner existiert
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Beim Start mehrmals versuchen, die DB-Tabellen anzulegen (MySQL braucht manchmal etwas Zeit)
    with app.app_context():
        for _ in range(10):
            try:
                db.create_all()
                seed_test_data() # Testdaten inserten
                break
            except OperationalError:
                time.sleep(2)
        else:
            raise OperationalError('Konnte nach mehreren Versuchen keine Verbindung zur Datenbank herstellen.')

    @app.route('/')
    def index():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        themen = Thema.query.all()
        tags = Tag.query.all()
        return render_template('index.html', themen=themen, tags=tags)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            benutzer = Benutzer.query.filter_by(EMail=email).first()
            if benutzer and check_password_hash(benutzer.PasswortHash or '', password):
                session['user_id'] = benutzer.BenutzerID
                session['role'] = benutzer.rolle.Bezeichnung
                session['user_name'] = f"{benutzer.Vorname} {benutzer.Nachname}"
                flash('Erfolgreich eingeloggt.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Ungültige Anmeldedaten.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Erfolgreich ausgeloggt.', 'success')
        return redirect(url_for('index'))

    @app.route('/search-materials')
    def search_materials():
        query = request.args.get('query', '').strip()
        tag_id = request.args.get('tag_id')
        thema_id = request.args.get('thema_id')

        q = Material.query
        if query:
            q = (
                q.join(Thema)
                 .outerjoin(Material.tags)
                 .filter(
                     or_(
                         Material.Dateiname.ilike(f'%{query}%'),
                         Thema.Bezeichnung.ilike(f'%{query}%'),
                         Tag.Bezeichnung.ilike(f'%{query}%')
                     )
                 )
            )
        if tag_id:
            q = q.join(Material.tags).filter(Tag.TagID == int(tag_id))
        if thema_id:
            q = q.filter(Material.ThemenID == int(thema_id))

        results = q.distinct().all() if (query or tag_id or thema_id) else []

        fav_ids = []
        if session.get('user_id'):
            fav_ids = [f.MaterialID for f in Favorit.query.filter_by(BenutzerID=session['user_id']).all()]

        return render_template('search_results.html', materials=results, favorit_ids=fav_ids)

    @app.route('/material/<int:material_id>')
    def material_detail(material_id):
        material = Material.query.get_or_404(material_id)
        kommentare = Kommentar.query \
            .filter_by(MaterialID=material_id) \
            .order_by(Kommentar.Erstelldatum.desc()) \
            .all()
        benutzer = Benutzer.query.all()
        fav_ids = []
        if session.get('user_id'):
            fav_ids = [f.MaterialID for f in Favorit.query.filter_by(BenutzerID=session['user_id']).all()]
        return render_template(
            'material_detail.html',
            material=material,
            kommentare=kommentare,
            benutzer=benutzer,
            favorit_ids=fav_ids
        )

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_material():
        if session.get('role') != 'Lehrkraft':
            flash('Nur Lehrkr\xc3\xa4fte k\xc3\xb6nnen Material hochladen.', 'danger')
            return redirect(url_for('index'))

        if request.method == 'POST':
            # Datei und Metadaten aus dem Formular auslesen
            datei = request.files.get('datei')
            autor_id = session.get('user_id')
            thema_id = request.form.get('thema_id')
            tags_raw = request.form.get('tags', '')

            if not datei or datei.filename == '':
                flash('Keine Datei ausgewählt.', 'danger')
                return redirect(request.url)

            filename = secure_filename(datei.filename)
            content = datei.read()
            size = len(content)
            dateityp = os.path.splitext(filename)[1].lstrip('.').lower()

            # Speichermodus bestimmen
            if size <= 1 * 1024 * 1024:
                # Datei ≤ 1 MB → in DB speichern
                neuer_material = Material(
                    Dateiname=filename,
                    Dateityp=dateityp,
                    AutorenID=int(autor_id),
                    ThemenID=int(thema_id),
                    SpeicherModus='BLOB',
                    Binaerdaten=content,
                    Dateipfad=None
                )
            else:
                # Datei > 1 MB → in uploads/-Ordner speichern
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                datei.seek(0)
                datei.save(filepath)
                neuer_material = Material(
                    Dateiname=filename,
                    Dateityp=dateityp,
                    AutorenID=int(autor_id),
                    ThemenID=int(thema_id),
                    SpeicherModus='PFAD',
                    Binaerdaten=None,
                    Dateipfad=filepath
                )

            # Tags verarbeiten (kommaseparierte Liste)
            tag_names = [t.strip() for t in tags_raw.split(',') if t.strip()]
            for name in tag_names:
                tag = Tag.query.filter_by(Bezeichnung=name).first()
                if not tag:
                    tag = Tag(Bezeichnung=name)
                    db.session.add(tag)
                    db.session.flush()  # Damit TagID generiert wird
                neuer_material.tags.append(tag)

            db.session.add(neuer_material)
            db.session.commit()
            flash('Material erfolgreich hochgeladen.', 'success')
            return redirect(url_for('material_detail', material_id=neuer_material.MaterialID))
        else:
            # GET: Formular anzeigen, dafür benötigen wir alle Themen
            themen = Thema.query.all()
            return render_template('upload.html', themen=themen)

    @app.route('/download/<int:material_id>')
    def download_material(material_id):
        material = Material.query.get_or_404(material_id)
        if material.SpeicherModus == 'BLOB':
            return send_file(
                BytesIO(material.Binaerdaten),
                download_name=material.Dateiname,
                as_attachment=True
            )
        else:
            return send_file(material.Dateipfad, as_attachment=True)

    @app.route('/add-comment/<int:material_id>', methods=['POST'])
    def add_comment(material_id):
        material = Material.query.get_or_404(material_id)
        autor_id = session.get('user_id') or request.form.get('autor_id')
        text = request.form.get('kommentartext').strip()

        if not text:
            flash('Kommentartext darf nicht leer sein.', 'danger')
            return redirect(url_for('material_detail', material_id=material_id))

        neuer_kommentar = Kommentar(
            MaterialID=material.MaterialID,
            AutorID=int(autor_id),
            Kommentartext=text,
            Erstelldatum=datetime.utcnow(),
            LetzteAenderung=datetime.utcnow()
        )
        db.session.add(neuer_kommentar)
        db.session.commit()
        flash('Kommentar hinzugefügt.', 'success')
        return redirect(url_for('material_detail', material_id=material_id))

    @app.route('/toggle-favorite/<int:material_id>', methods=['POST'])
    def toggle_favorite(material_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        fav = Favorit.query.filter_by(BenutzerID=session['user_id'], MaterialID=material_id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
        else:
            new_fav = Favorit(BenutzerID=session['user_id'], MaterialID=material_id)
            db.session.add(new_fav)
            db.session.commit()
        return redirect(request.referrer or url_for('index'))

    @app.route('/favoriten')
    def favoriten():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        items = (Material.query
                 .join(Favorit)
                 .filter(Favorit.BenutzerID == session['user_id'])
                 .all())
        return render_template('favoriten.html', materials=items)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
