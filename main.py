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

    episode_info = get_audio_url(job['feedUrl'], job['episode'])

    if episodeInfo == None:
        save_job({
            'id': jobId,
            'status': 'FAILED',
            'failMsg': 'could not find RSS feed or episode'
        })
        return

    job['episodeInfo'] = episode_info

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

def extract_chapters(url):
    import subprocess
    out = subprocess.run(['ffprobe', '-i', url,  '-print_format', 'json', '-show_chapters', '-loglevel' , 'error'], stdout=subprocess.PIPE, encoding='utf-8')
    return json.loads(out.stdout)['chapters']

# action functions called from CLI
def run_action(args):
    jobId = create_job(args.url, args.language, args.episode)
    start_job(jobId)

def transcribe_action(args):
    from transcribe.parse_rss import get_audio_url
    from transcribe.SpeechToTextModules.GoogleSpeechAPI import GoogleSpeechToText

    # init Google Speech API
    stt = GoogleSpeechToText('/home/lukas/Documents/cred.json', 'transcribe-buffer')

    episode_info = get_audio_url(args.url, args.episode)

    # download audio
    original_audio_file_path = download_audio(episode_info['episodeUrl'])

    # transcribe
    tokens, boundaries = stt.transcribe(original_audio_file_path, args.language)

    # save transcript to file
    transcript_file = f'{args.output}/{os.path.basename(episode_info["episodeUrl"])}_transcript.json'
    with open(transcript_file, 'w') as f:
        json.dump({
            'boundaries': boundaries,
            'tokens': [token.to_dict() for token in tokens],
            'chapters': extract_chapters(episode_info['episodeUrl']) if args.chapters else []
        }, f)

def chapterize_action(args):
    from transcribe.SpeechToTextModules.SpeechToTextModule import TranscriptToken
    from chapterize.cosine_similarity import cosine_similarity

    with open(args.transcript, 'r') as f:
        transcript = json.load(f)

    tokens = [TranscriptToken(token['token'], token['time']) for token in transcript['tokens']]
    boundaries = transcript['boundaries']

    chapters = cosine_similarity(
        tokens,
        boundaries,
        language=args.language,
        title_tokens=args.title_tokens,
        window_width=args.window_width,
        max_utterance_delta=args.max_utterance_delta,
        tfidf_min_df=args.tfidf_min_df,
        tfidf_max_df=args.tfidf_max_df,
        savgol_window_length=args.savgol_window_length,
        savgol_polyorder=args.savgol_polyorder,
        visual=args.v
    )  
    
    
# if called directly, parse comand line arguments
if __name__ == '__main__':
    # top-level parser
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(help='possible actions')

    # main parser 'run'
    run_parser = subparsers.add_parser('run', help='create chapters for a podcast episode from an RSS feed URL')
    run_parser.add_argument('url', type=str, help='RSS feed URL for the podcast')
    run_parser.add_argument('-e', '--episode', type=int, default=0, help='default: 0; Number of episode to chapterize (0 for latest, 1 for penultimate)')
    run_parser.add_argument('-l', '--language', type=str, required=True, choices=['en', 'de'], help='Language of podcast episode')
    run_parser.set_defaults(func=run_action)

    # transcribe parser
    transcribe_parser = subparsers.add_parser('transcribe', help='transcribe a podcast episode from an RSS feed URL')
    transcribe_parser.add_argument('url', type=str, help='RSS feed URL for the podcast')
    transcribe_parser.add_argument('-e', '--episode', type=int, default=0, help='default: 0; Number of episode to transcribe (0 for latest, 1 for penultimate)')
    transcribe_parser.add_argument('-l', '--language', type=str, required=True, choices=['en', 'de'], help='Language of podcast episode')
    transcribe_parser.add_argument('-c', '--chapters', action='store_true', help='extract chapters from audio file')
    transcribe_parser.add_argument('output', type=str, default='.', help='output directory')
    transcribe_parser.set_defaults(func=transcribe_action)

    # chapterize parser
    from chapterize.cosine_similarity import default_params
    chapterize_parser = subparsers.add_parser('chapterize', help='create chapters from an audio transcript')
    chapterize_parser.add_argument('transcript', type=str, help='transcript json file incl. tokens and boundaries')
    chapterize_parser.add_argument('-l', '--language', type=str, required=True, choices=['en', 'de'], help='Language of podcast episode')
    chapterize_parser.add_argument('-v', action='store_true', help='show graph')
    chapterize_parser.add_argument('-title-tokens', type=int, default=6, help='number of tokens to generate for each chapter title')
    chapterize_parser.add_argument('-window-width', type=int, default=default_params.window_width, help='window width for inital segmentation')
    chapterize_parser.add_argument('-max-utterance-delta', type=int, default=default_params.max_utterance_delta, help='maximum delta of tokens when refining detected boundaries by choosing nearby utterance boundaries')
    chapterize_parser.add_argument('-tfidf-min-df', type=int, default=default_params.tfidf_min_df, help='tfidf min_df value')
    chapterize_parser.add_argument('-tfidf-max-df', type=int, default=default_params.tfidf_max_df, help='tfidf max_df value')
    chapterize_parser.add_argument('-savgol-window-length', type=int, default=default_params.savgol_window_length, help='window_length value for savgol smoothing')
    chapterize_parser.add_argument('-savgol-polyorder', type=int, default=default_params.savgol_polyorder, help='polyorder value for savgol smoothing')
    chapterize_parser.set_defaults(func=chapterize_action)

    args = parser.parse_args()
    
    # run action function referenced in 'func' attribute
    args.func(args)
