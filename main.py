from transcribe.parse_rss import getAudioUrl
from transcribe.transcribe_google import transcribeAudioFromUrl
from chapterize.cosine_similarity import cosine_similarity
from write_chapters import write_chapters

import uuid
import os
import json

def saveJob(_job):
    with open('jobs.json', 'r+') as f:
        if not os.stat(f.fileno()).st_size == 0:
            jobs = json.load(f)
        else:
            jobs = []

        updated = False
        for job in jobs:
            if job["id"] == _job['id']:
                job.update(_job)
                print('job found, updating info')
        
        if not updated:
            print('job not found, adding job')
            jobs.append(_job)
        json.dump(jobs, f)

feedUrl = input('feed url: ')
episode = input('episode no (0 for latest): ')


if episode != '':
    episodeInfo = getAudioUrl(feedUrl, int(episode))
else:
    episodeInfo = getAudioUrl(feedUrl)

# create job object
# possible status states: 'CREATED', 'TRANSCRIBING', 'TRANSCRIBED', 'NLP', 'CHAPTER_WRITTEN', 'DONE'

jobId = str(uuid.uuid1())
job = {
    'id': jobId,
    'feedUrl': feedUrl,
    'episodeUrl': episodeInfo['episodeUrl'],
    'episodeTitle': episodeInfo['episodeTitle'],
    'feedAuthor': episodeInfo['author'],
    'status': 'TRANSCRIBING'
}

saveJob(job)

paths = transcribeAudioFromUrl(episodeInfo['episodeUrl'])
# paths: [originalAudioPath, wavAudioPath, gcsUri]

job['originalAudioFilePath'] = paths['originalAudioFilePath']
job['wavAudioFilePath'] = paths['wavAudioFilePath']
job['transcriptFile'] = paths['transcriptFile']
job['gcsUri'] = paths['gcsUri']
job['status'] = 'TRANSCRIBED'

saveJob(job)

boundaries = cosine_similarity(job['transcriptFile'])

# create generic chapter names 
chapters = [[boundary, 'chapter ' + str(idx+1)] for idx, boundary in enumerate(boundaries)]

write_chapters(chapters, job['originalAUdioFile'])