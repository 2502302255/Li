import os
import click
from flask import Flask, render_template
from flask.cli import with_appcontext
from rsshub.config import config
from rsshub.extensions import *
from rsshub.blueprints.main import bp as main_bp
from rsshub.utils import XMLResponse


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.response_class = XMLResponse

    register_blueprints(app)
    register_extensions(app)
    register_errors(app)
    register_cli(app)

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    debugtoolbar.init_app(app)
    moment.init_app(app)


def register_blueprints(app):
    app.register_blueprint(main_bp)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


def register_cli(app):
    @app.cli.command()
    @with_appcontext
    def ptshell():
        """Use ptpython as shell."""
        try:
            from ptpython.repl import embed
            if not app.config['TESTING']:
                embed(app.make_shell_context())
        except ImportError:
            click.echo('ptpython not installed! Use the default shell instead.')