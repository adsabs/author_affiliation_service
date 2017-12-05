#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import inspect

from adsmutils import ADSFlask, load_module

import authoraffsrv
from authoraffsrv.views import bp

def create_app(config=None):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    proj_home = os.path.dirname(inspect.getsourcefile(authoraffsrv))
    local_config = load_module(os.path.abspath(os.path.join(proj_home, 'config.py')))

    app = ADSFlask(__name__, static_folder=None, proj_home=proj_home, local_config=local_config)
    app.url_map.strict_slashes = False

    app.register_blueprint(bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
