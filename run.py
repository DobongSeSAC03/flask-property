import os
from myapp import create_app
from flask_debugtoolbar import DebugToolbarExtension

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)
DebugToolbarExtension(app)

if __name__ == '__main__':
    app.run()
