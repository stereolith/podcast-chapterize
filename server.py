from flask import Flask, jsonify, request, abort
from flask_cors import CORS

from transcribe.parse_rss import getEpisodes

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/episodes', methods=['GET'])
def episodes():
    rssUrl = request.args.get('rssurl')
    episodes = getEpisodes(rssUrl)
    if episodes == 0:
        abort(404)
    else:
        response_object = {'status': 'success'}
        response_object['episodes'] = [{'label': episode, 'index': idx} for idx, episode in enumerate(episodes)]
        return jsonify(response_object)

if __name__ == '__main__':
    app.run()
