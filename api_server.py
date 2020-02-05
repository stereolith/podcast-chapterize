from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS

from api.utils import utils
from api.core import core

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# register blueprints
app.register_blueprint(core)
app.register_blueprint(utils)

@app.route('/output/<path:filename>')
def download_file(filename):
    return send_from_directory('output/', filename)

if __name__ == '__main__':
    app.run()

