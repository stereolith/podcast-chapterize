import feedparser

def getAudioUrl(feedUrl, episode=0):
    feed = feedparser.parse(feedUrl)
    try:
        lastEposide = feed['entries'][episode]
        for link in lastEposide['links']:
            if link['rel'] == 'enclosure':
                audioUrl = link['href']
        if audioUrl.rfind('?') != -1:
            audioUrl = audioUrl[:audioUrl.rfind('?')]
        print('episode name: ', lastEposide['title'])
        print('audio file url: ', audioUrl)
        return audioUrl

    except IndexError:
        print('could not find feed')

