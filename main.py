import argparse
import os
from shutil import copyfile
import json
import time
import uuid
import wget
import pprint
import subprocess
from tinydb import TinyDB, Query

pp = pprint.PrettyPrinter(indent=4)

# create tinydb
db = TinyDB('jobs.json')
Job = Query()


def save_job(_job):
    if len(db.search(Job.id == _job['id'])) != 0:
        db.update(_job, Job.id == _job['id'])
    else:
        db.insert(_job)
    print('new status: ')
    print(pp.pprint(db.search(Job.id == _job['id'])[0]))

def get_job(id):
    job = db.search(Job.id == id)
    if len(job) == 0 or len(job) > 1:
        return None
    else:
        return job[0]

def create_job(feedUrl, language, episode=0):
    jobId = str(uuid.uuid1())

    # possible status states: 'CREATED', 'TRANSCRIBING', 'TRANSCRIBED', 'NLP', 'CHAPTER_WRITTEN', 'DONE'
    save_job({'id': jobId, 'status': 'CREATED'})

    job = {
        'id': jobId,
        'feedUrl': feedUrl,
        'language': language,
        'episode': episode,
        'status': 'TRANSCRIBING'
    }
    save_job(job)

    return job['id']

def start_job(jobId, keep_temp=False):
    from transcribe.parse_rss import get_audio_url
    from transcribe.SpeechToTextModules.GoogleSpeechAPI import GoogleSpeechToText
    from chapterize.cosine_similarity import cosine_similarity
    from write_chapters import ChapterWriter

    # init Google Speech API
    stt = GoogleSpeechToText('/home/lukas/Documents/cred.json', 'transcribe-buffer')

    # init chapter writer
    cw = ChapterWriter()

    job = get_job(jobId)

    episodeInfo = get_audio_url(job['feedUrl'], job['episode'])

    if episodeInfo == None:
        save_job({
            'id': jobId,
            'status': 'FAILED',
            'failMsg': 'could not find RSS feed or episode'
        })
        return

    job['episodeInfo'] = episodeInfo

    save_job(job)

    # download audio
    job['originalAudioFilePath'] = download_audio(job['episodeInfo']['episodeUrl'])

    # transcribe
    tokens, boundaries = stt.transcribe(job['originalAudioFilePath'], job['language'])

    # save transcript to file
    job['transcriptFile'] = 'output/' + os.path.basename(job['episodeInfo']['episodeUrl']) + '_transcript.json'
    with open(job['transcriptFile'], 'w') as f:
        json.dump({
            'boundaries': boundaries,
            'tokens': [token.to_dict() for token in tokens]
        }, f)

    save_job(job)

    chapters = cosine_similarity(tokens, boundaries, language=job['language'], visual=False)

    save_job({
        'id': jobId,
        'status': 'WRITING CHAPTERS'
    })

    # write chapters to job object
    save_job({
        'id': jobId, 
        'chapters': [chapter.to_dict() for chapter in chapters]
    })

    # write chapters to file, convert if neccecary
    processed_audio_file_path = os.path.join('output/', os.path.basename(job['originalAudioFilePath']))
    copyfile(job['originalAudioFilePath'], processed_audio_file_path )

    suffix = os.path.splitext(processed_audio_file_path)[1]
    if suffix == '.mp3':
        cw.write_chapters('mp3', chapters, processed_audio_file_path)
    elif suffix == '.m4a':
        cw.write_chapters('m4a', chapters, processed_audio_file_path)
    else:
        mp3_file_path = os.path.splitext(processed_audio_file_path) + '.mp3'
        subprocess.Popen(f'ffmpeg -y -i {processed_audio_file_path} {mp3_file_path}', shell=True)
        processed_audio_file_path = mp3_file_path

    cw.write_chapters('txt', chapters, processed_audio_file_path + '.txt')

    save_job({
        'id': jobId,
        'chaptersFilePath': processed_audio_file_path.replace('.mp3', '_chapters.txt'),
        'processedAudioFilePath': processed_audio_file_path,
        'status': 'DONE'
    })

    # remove temp files
    if not keep_temp:
        os.remove(job['originalAudioFilePath'])


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


def download_audio(url):
    filename = str(uuid.uuid1()) + os.path.basename(url)
    if not os.path.exists('transcribe/download'):
        os.makedirs('transcribe/download')
    wget.download(url, out='transcribe/download/' + filename)
    path = os.path.join('transcribe/download', filename)
    print('\ndownloaded file {0}'.format(path))
    return path


# if called directly, parse comand line arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='RSS feed URL for the podcast')
    parser.add_argument('language', type=str, choices=['en', 'de'], help='Language of podcast episode')
    parser.add_argument('-e', '--episode', type=int, default=0, help='default: 0; Number of episode to chapterize (0 for latest, 1 for penultimate)')

    args = parser.parse_args()
    
    jobId = create_job(args.url, args.language, args.episode)
    start_job(jobId)
    