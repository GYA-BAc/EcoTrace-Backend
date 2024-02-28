import os

from flask import Flask

#flask --app flaskr run --debug

def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__, 
        instance_relative_config=True, 
        instance_path=os.path.join(__path__[0], 'instance')
    )
    
    # print(app.instance_path)
    # print(__path__)
    # exit()
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup with factory function
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import posts
    app.register_blueprint(posts.bp)

    return app