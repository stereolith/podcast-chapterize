# This flask blueprint includes core api endpoints for creating 
# a chapterization job and fetching the status of a job

from flask import Flask, jsonify, request, Blueprint
import validators
import uuid
import threading

from main import start_job, get_job

core = Blueprint('core',  __name__)

# start transcription job (POST) / get job info (GET)
@core.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'POST':
        jobId = str(uuid.uuid1())
        post_data = request.get_json()
        if not post_data:
            return response_json('failure', {'post_data': 'Could not get POST data'})

        feedUrl = post_data.get('feedUrl')
        episode = post_data.get('episode')
        language = post_data.get('language')

        if None in [feedUrl, episode, language]:
            data = {}
            if feedUrl is None:
                data['feedUrl'] = 'feedUrl is required'
            if episode  is None:
                data['episode'] = 'episode is required'
            if language is None:
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