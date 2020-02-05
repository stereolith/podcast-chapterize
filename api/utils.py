# this flask blueprint includes utitlity api endpoints for:
#   * extracting language from RSS feed
#   * extracting episode titles from RSS feed
#   * generting podlove player config JSON

from flask import Flask, jsonify, request, Blueprint
import validators

from transcribe.parse_rss import get_episodes, get_language
from main import get_player_config

utils = Blueprint('utils',  __name__)

# get episodes from RSS URL
@utils.route('/episodes', methods=['GET'])
def episodes():
    rssUrl = request.args.get('rssurl')
    if not rssUrl:
        return response_json('failure', {'rssUrl': 'rssUrl is required'})
    if not validators.url(rssUrl):
        return response_json('failure', {'rssUrl': 'Not a valid URL'})

    episodes = get_episodes(rssUrl)

    if episodes == 0 or len(episodes) == 0:
        return response_json('error', 'Could not find RSS feed')
    else:
        return response_json('success', {
            'episodes': [{'label': episode, 'index': idx} for idx, episode in enumerate(episodes)]
        })

# try to extract language from RSS feed
@utils.route('/feed-lang', methods=['GET'])
def feed_lang():
    rssUrl = request.args.get('rssurl')

    if not rssUrl:
        return response_json('failure', {'rssUrl': 'rssUrl is required'})
    if not validators.url(rssUrl):
        return response_json('failure', {'rssUrl': 'Not a valid URL'})

    lang = get_language(rssUrl)
    if lang == 0:
        return response_json('error', 'Could not determine feed language')
    else:
        return response_json('success', {'language': lang})


# get podlove player config
@utils.route('/player-config', methods=['GET'])
def config():
    jobId = request.args.get('id')
    if not jobId:
        return response_json('failure', {'id': 'id is required'})

    config = get_player_config(jobId)
    if config == None:
        return response_json('error', 'no job found with this id')
    else:
        return response_json('success', {'config': config})


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
        