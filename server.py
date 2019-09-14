from flask import Flask, jsonify, request, abort, Response, send_from_directory
from flask_cors import CORS

import uuid
import threading

from transcribe.parse_rss import getEpisodes, getLanguage
from main import start_job, get_job, get_player_config

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# get episodes from RSS URL
@app.route('/episodes', methods=['GET'])
def episodes():
    rssUrl = request.args.get('rssurl')
    episodes = getEpisodes(rssUrl)
    if episodes == 0 or len(episodes) == 0:
        abort(404)
    else:
        response_object = {'status': 'success'}
        response_object['episodes'] = [{'label': episode, 'index': idx} for idx, episode in enumerate(episodes)]
        return jsonify(response_object)
        
@app.route('/feed-lang', methods=['GET'])
def feedLang():
    rssUrl = request.args.get('rssurl')
    lang = getLanguage(rssUrl)
    if lang == 0:
        abort(404)
    else:
        response_object = {'status': 'success', 'language': lang}
        return jsonify(response_object)

# start transcription job (POST) / get job info (GET)
@app.route('/job', methods=['GET', 'POST'])
def job():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        jobId = str(uuid.uuid1())
        post_data = request.get_json()
        feedUrl = post_data.get('feedUrl')
        episode = post_data.get('episode')
        language = post_data.get('language')
        if feedUrl == None or episode == None or language == None:
            abort(400)
        else:
            response_object['jobId'] = jobId
            thread = threading.Thread(target=start_job, args=(jobId, feedUrl, language, int(episode),))
            thread.start()
    else:
        job = get_job(request.args.get('id'))
        if job == None:
            abort(404)
        else:
            response_object['job'] = job
    return jsonify(response_object)


# get podlove player config
@app.route('/player-config', methods=['GET'])
def config():
    config = get_player_config(request.args.get('id'))
    if config == None:
        abort(404)
    else:
        response_object = {'status': 'success'}
        response_object['config'] = config
        return jsonify(response_object)

@app.route('/output/<path:filename>')
def download_file(filename):
    return send_from_directory('output/', filename)

if __name__ == '__main__':
    app.run()
