import os

from flask import Flask, jsonify

from . import db


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("TRAILHEAD_DB", "trailhead.db"),
    )
    if config:
        app.config.update(config)

    app.teardown_appcontext(db.close_db)

    from .catalog import bp as catalog_bp
    from .orders import bp as orders_bp

    app.register_blueprint(catalog_bp)
    app.register_blueprint(orders_bp)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app
