import os
import sys
from flask import Flask
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, folder)
from voto.data.db_session import initialise_database
app = Flask(__name__)


def main():
    configure()
    app.run(debug=True, port=5006)


def configure():
    print("Configuring Flask app:")

    register_blueprints()
    print("Registered blueprints")

    initialise_database()
    print("DB setup completed.")
    print("", flush=True)


def register_blueprints():
    from voto.views import home_views
    app.register_blueprint(home_views.blueprint)


if __name__ == '__main__':
    main()
else:
    configure()
