

import argparse
import os
from shutil import copyfile
import json
import time
import uuid

from tinydb import TinyDB, Query

# create tinydb
db = TinyDB('jobs.json')
Job = Query()

def save_job(_job):
    if len(db.search(Job.id == _job['id'])) != 0:
        db.update(_job, Job.id == _job['id'])
    else:
        db.insert(_job)
    print('new status: ')
    print(db.search(Job.id == _job['id']))

def get_job(id):
    job = db.search(Job.id == id)
    if len(job) == 0 or len(job) > 1:
        return None
    else:
        return job[0]


def start_job(jobId, feedUrl, episode=0):
    from transcribe.parse_rss import getAudioUrl
    from transcribe.transcribe_google import transcribeAudioFromUrl
    from chapterize.cosine_similarity import cosine_similarity
    from write_chapters import write_chapters

    # possible status states: 'CREATED', 'TRANSCRIBING', 'TRANSCRIBED', 'NLP', 'CHAPTER_WRITTEN', 'DONE'
    save_job({'id': jobId, 'status': 'CREATED'})

    # check if google cloud credentials env var is set
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') == None:
        save_job({'id': jobId, 'status': 'FAILED', 'failMsg': 'Google Cloud credential env var not set'})
        return

    episodeInfo = getAudioUrl(feedUrl, episode)

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

    job = {
        'id': jobId,
        'originalAudioFilePath': paths['originalAudioFilePath'],
        'wavAudioFilePath': paths['wavAudioFilePath'],
        'transcriptFile': paths['transcriptFile'],
        'gcsUri': paths['gcsUri'],
        'status': 'NLP'
    }
    save_job(job)

    chapters = cosine_similarity(job['transcriptFile'], visual=False)

    save_job({'id': jobId, 'status': 'WRITING CHAPTERS'})

    # write chapters to job onject
    save_job({'id': jobId, 'chaptersFilePath': job['originalAudioFilePath'] + '_chapters.txt', 'chapters': chapters})

    # copy episode file to output folder
    processedAudioFilePath = os.path.join('output/', os.path.basename(job['originalAudioFilePath']))
    copyfile(job['originalAudioFilePath'], processedAudioFilePath )

    write_chapters(chapters, job['originalAudioFilePath'])


    save_job({'id': jobId, 'processedAudioFilePath': processedAudioFilePath, 'status': 'DONE'})


def get_player_config(id):

    job = get_job(id)

    if job == None:
        return None

    chapters = [{
        'start': time.strftime('%H:%M:%S', time.gmtime(chapter['time'])),
        'title': chapter['name']
    } for chapter in job['chapters']]

    fileSize = os.path.getsize(job['processedAudioFilePath'])

    print(job['processedAudioFilePath'])
    
    return {
        'title': job['episodeTitle'],
        'subtitle': 'subtitle',
        'summary': 'summary',
        'publicationDate': '2016-02-11T03:13:55+00:00',
        'poster': '',
        'show': {
            'title': 'Show Title',
            'url': 'https://showurl.fm'
        },
        'chapters': chapters,
        'audio': [{
          'url': job['processedAudioFilePath'],
          'mimeType': 'audio/mp3',
          'size': fileSize,
          'title': 'Audio MP3'
        }],
        'reference': {
            'base': '/js/web-player/'
        }
    }


# if called directly, parse comand line arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='RSS feed URL for the podcast.')
    parser.add_argument('-e', '--episode', type=int, default=0, help='default: 0; Number of episode to chapterize (0 for latest, 1 for penultimate)')
    args = parser.parse_args()
    
    jobId = str(uuid.uuid1())
    start_job(jobId, args.url, args.episode)