from flask import Flask, jsonify, request, abort, Response
from flask_cors import CORS

import uuid
import threading

from transcribe.parse_rss import getEpisodes
from main import start_job, get_job

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

# start transcription job
@app.route('/job', methods=['POST'])
def job():
        jobId = str(uuid.uuid1())
        post_data = request.get_json()
        feedUrl = post_data.get('feedUrl')
        episode = post_data.get('episode')
        if feedUrl == None or episode == None:
            abort(400)
        else:
            response_object = {'status': 'success', 'jobId': jobId}
            thread = threading.Thread(target=start_job, args=(jobId, feedUrl, episode,))
            thread.start()
            return jsonify(response_object)


# get job status
@app.route('/status', methods=['GET'])
def status():
    status = get_job(request.args.get('id'))
    if(len(status) == 0):
        abort(404)
    else:
        response_object = {'status': 'success'}
        response_object['status'] = status[0]
        return jsonify(response_object)

if __name__ == '__main__':
    app.run()
