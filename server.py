from flask import Flask, jsonify, request, abort, Response, send_from_directory
from flask_cors import CORS

import validators
import uuid
import threading

from transcribe.parse_rss import getEpisodes, getLanguage
from main import start_job, get_job, get_player_config

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# get episodes from RSS URL
@app.route('/episodes', methods=['GET'])
def episodes():
    rssUrl = request.args.get('rssurl')
    if not rssUrl:
        return response_json('failure', {'rssUrl': 'rssUrl is required'})
    if not validators.url(rssUrl):
        return response_json('failure', {'rssUrl': 'Not a valid URL'})

    episodes = getEpisodes(rssUrl)

    if episodes == 0 or len(episodes) == 0:
        return response_json('error', {'rssUrl': 'Could not find RSS feed'})
    else:
        return response_json('success', {
            'episodes': [{'label': episode, 'index': idx} for idx, episode in enumerate(episodes)]
        })

# try to extract language from RSS feed
@app.route('/feed-lang', methods=['GET'])
def feed_lang():
    rssUrl = request.args.get('rssurl')

    if not rssUrl:
        return response_json('failure', {'rssUrl': 'rssUrl is required'})
    if not validators.url(rssUrl):
        return response_json('failure', {'rssUrl': 'Not a valid URL'})

    lang = getLanguage(rssUrl)
    if lang == 0:
        return response_json('error', 'Could not determine feed language')
    else:
        return response_json('success', {'language': lang})

# start transcription job (POST) / get job info (GET)
@app.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'POST':
        jobId = str(uuid.uuid1())
        post_data = request.get_json()
        if not post_data:
            return response_json('failure', {'post_data': 'Could not get POST data'})

        feedUrl = post_data.get('feedUrl')
        episode = post_data.get('episode')
        language = post_data.get('language')

        if not all([feedUrl, episode, language]):
            data = {}
            if not feedUrl:
                data['feedUrl'] = 'feedUrl is required'
            if not episode:
                data['episode'] = 'episode is required'
            if not language:
                data['language'] = 'language is required'
            return response_json('failure', data)
        else:
            thread = threading.Thread(target=start_job, args=(jobId, feedUrl, language, int(episode),))
            thread.start()
            return response_json('success', {'jobId': jobId})
    else:
        jobId = request.args.get('id')
        if not jobId:
            return response_json('failure', {'id': 'id is required'})
        job = get_job(jobId)
        if job == None:
            return response_json('error', 'no job found with this id')
        else:
            return response_json('success', {'job': job})


# get podlove player config
@app.route('/player-config', methods=['GET'])
def config():
    jobId = request.args.get('id')
    if not jobId:
        return response_json('failure', {'id': 'id is required'})

    config = get_player_config(jobId)
    if config == None:
        return response_json('error', 'no job found with this id')
    else:
        return response_json('success', {'config': config})

@app.route('/output/<path:filename>')
def download_file(filename):
    return send_from_directory('output/', filename)

if __name__ == '__main__':
    app.run()

# JSON response helper, according to jsend guidelines
def response_json(status, data):
    if status == 'error':
        return jsonify({
            'status': status,
            'message': data
        })
    else:
        return jsonify({
            'status': status,
            'data': data
        })