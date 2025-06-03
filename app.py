import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError

from config import Config
from models import db, Rolle, Benutzer, Thema, Material, Version, Tag, Kommentar

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
                break
            except OperationalError:
                time.sleep(2)
        else:
            raise OperationalError('Konnte nach mehreren Versuchen keine Verbindung zur Datenbank herstellen.')

    @app.route('/')
    def index():
        # Für die Live-Suche brauchen wir nur die Suchleiste (Themen/Benutzer für Dropdown werden bei Upload benötigt)
        return render_template('index.html')

    @app.route('/search-materials')
    def search_materials():
        query = request.args.get('query', '').strip()
        if query:
            # JOIN Material → Thema und → Tag, dann Filter auf Dateiname, Themen-Bezeichnung oder Tag-Bezeichnung
            results = (
                Material.query
                .join(Thema)  # Material.ThemenID = Thema.ThemaID
                .outerjoin(Material.tags)  # Material.tags → Tag (über material_tag-Zwischentabelle)
                .filter(
                    or_(
                        Material.Dateiname.ilike(f'%{query}%'),
                        Thema.Bezeichnung.ilike(f'%{query}%'),
                        Tag.Bezeichnung.ilike(f'%{query}%')
                    )
                )
                .distinct()
                .all()
            )
        else:
            results = []

        # Gibt nur das Teilergebnis-Fragment zurück, nicht die gesamte Basis-Seite
        return render_template('search_results.html', materials=results)

    @app.route('/material/<int:material_id>')
    def material_detail(material_id):
        material = Material.query.get_or_404(material_id)
        kommentare = Kommentar.query \
            .filter_by(MaterialID=material_id) \
            .order_by(Kommentar.Erstelldatum.desc()) \
            .all()
        benutzer = Benutzer.query.all()
        return render_template(
            'material_detail.html',
            material=material,
            kommentare=kommentare,
            benutzer=benutzer
        )

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_material():
        if request.method == 'POST':
            # Datei und Metadaten aus dem Formular auslesen
            datei = request.files.get('datei')
            autor_id = request.form.get('autor_id')
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
            # GET: Formular anzeigen, dafür benötigen wir alle Themen und Benutzer
            themen = Thema.query.all()
            benutzer = Benutzer.query.all()
            return render_template('upload.html', themen=themen, benutzer=benutzer)

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
        autor_id = request.form.get('autor_id')
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
