from app import create_app
from testdata import seed_test_data

app = create_app()
with app.app_context():
    seed_test_data()
    print("Testdaten wurden erfolgreich angelegt.")
