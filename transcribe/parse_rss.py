import feedparser

def getAudioUrl(feedUrl, episode=0):
    feed = feedparser.parse(feedUrl)
    try:
        lastEpisode = feed['entries'][episode]
        for link in lastEpisode['links']:
            if link['rel'] == 'enclosure':
                audioUrl = link['href']
        if audioUrl.rfind('?') != -1:
            audioUrl = audioUrl[:audioUrl.rfind('?')]
        print('episode name: ', lastEpisode['title'])
        print('audio file url: ', audioUrl)
        return {
            'episodeUrl': audioUrl,
            'episodeTitle': lastEpisode['title'],
            'author': lastEpisode['author']
        }
    except IndexError:
        print('could not find feed')

