import feedparser

def get_audio_url(feedUrl, episode=0):
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
            'author': lastEpisode['author'] if 'author' in lastEpisode else ""
        }
    except IndexError:
        print('could not find feed')
        return None

def get_episodes(feedUrl, last=10):
    try:
        feed = feedparser.parse(feedUrl)
        episodes = feed['entries'][:last]
        if feed['feed'] == {}: return 0
        return [episode['title'] for episode in episodes]
    except IndexError:
        print('could not find all last episodes')
        return 0
    
def get_language(feedUrl):
    try:
        feed = feedparser.parse(feedUrl)
        return feed['feed']['language'][0:2]
    except KeyError:
        print('could not find feed or language key')
        return 0