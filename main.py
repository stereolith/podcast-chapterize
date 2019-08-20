from transcribe.parse_rss import getAudioUrl
from transcribe.transcribe_google import transcribeAudioFromUrl
from chapterize.cosine_similarity import cosine_similarity
from write_chapters import write_chapters

import os
import json

from tinydb import TinyDB, Query

# create tinydb
db = TinyDB('jobs.json')
Job = Query()

def save_job(_job):
    if len(db.search(Job.id == _job['id'])) != 0:
        db.update(_job, Job.id == _job['id'])
    else:
        db.insert(_job)

def get_job(id):
    return db.search(Job.id == id)


def start_job(jobId, feedUrl, episode=''):

    

    # possible status states: 'CREATED', 'TRANSCRIBING', 'TRANSCRIBED', 'NLP', 'CHAPTER_WRITTEN', 'DONE'
    save_job({'id': jobId, 'status': 'CREATED'})

    # check if google cloud credentials env var is set
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') == None:
        save_job({'id': jobId, 'status': 'FAILED', 'failMsg': 'Google Cloud credential env var not set'})
        return

    if episode != '':
        episodeInfo = getAudioUrl(feedUrl, int(episode))
    else:
        episodeInfo = getAudioUrl(feedUrl)

    if episodeInfo == None:
        save_job({'id': jobId, 'status': 'FAILED', 'failMsg': 'could not find RSS feed or episode'})
        return

    job = {
        'id': jobId,
        'feedUrl': feedUrl,
        'episodeUrl': episodeInfo['episodeUrl'],
        'episodeTitle': episodeInfo['episodeTitle'],
        'feedAuthor': episodeInfo['author'],
        'status': 'TRANSCRIBING'
    }
    save_job(job)

    paths = transcribeAudioFromUrl(episodeInfo['episodeUrl'])
    # paths: [originalAudioPath, wavAudioPath, gcsUri]

    job['originalAudioFilePath'] = paths['originalAudioFilePath']
    job['wavAudioFilePath'] = paths['wavAudioFilePath']
    job['transcriptFile'] = paths['transcriptFile']
    job['gcsUri'] = paths['gcsUri']
    job['status'] = 'NLP'

    save_job(job)

    boundaries = cosine_similarity(job['transcriptFile'])

    save_job({'id': jobId, 'status': 'WRITING CHAPTERS'})

    # create generic chapter names 
    chapters = [[boundary, 'chapter ' + str(idx+1)] for idx, boundary in enumerate(boundaries)]

    write_chapters(chapters, job['originalAudioFile'])

    save_job({'id': jobId, 'status': 'DONE'})


#feedUrl = input('feed url: ')
#episode = input('episode no (0 for latest): ')

#start_job(feedUrl, episode)