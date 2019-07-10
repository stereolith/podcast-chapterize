from transcribe.parse_rss import getAudioUrl
from transcribe.transcribe_google import transcribeAudioFromUrl
from lda_json import lda_json

feedUrl = input("feed url: ")
episode = input("episode no (0 for latest): ")
if episode != '':
    url = getAudioUrl(feedUrl, int(episode))
else:
    url = getAudioUrl(feedUrl)

filename = transcribeAudioFromUrl(url)

lda_json('transcribe/transcripts/' + filename + '.json')