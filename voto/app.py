import os
import sys
import logging
import json
from flask import Flask

_log = logging.getLogger(__name__)

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)
from voto.data.db_session import initialise_database

# Store credentials in a external file that is never added to git or shared over insecure channels
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)

app = Flask(__name__)


def main():
    configure()
    app.run(debug=True, port=5006)


def configure(local=False):
    _log.info("Configuring Flask app:")

    register_blueprints()
    _log.info("Registered blueprints")
    if local:
        initialise_database(user=None, password=None)
    else:
        initialise_database(
            user=secrets["mongo_user"],
            password=secrets["mongo_password"],
            port=int(secrets["mongo_port"]),
            server=secrets["mongo_server"],
            db=secrets["mongo_db"],
        )
    _log.info("DB setup completed.")


def register_blueprints():
    from voto.views import home_views, mission_views, platform_views

    app.register_blueprint(home_views.blueprint)
    app.register_blueprint(mission_views.blueprint)
    app.register_blueprint(platform_views.blueprint)


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/voto.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
else:
    configure()
