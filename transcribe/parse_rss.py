import feedparser

def get_audio_url(feed_url, episode=0):
    feed = feedparser.parse(feed_url)

    try:
        last_episode = feed['entries'][episode]

        audio_url = ''
        for link in last_episode['links']:
            if link['rel'] == 'enclosure':
                audio_url = link['href']

        if audio_url == '':
            print('could not find audio url')
            return None

        if audio_url.rfind('?') != -1:
            audio_url = audio_url[:audio_url.rfind('?')]
        print('episode name: ', last_episode['title'])
        print('audio file url: ', audio_url)
        return {
            'episodeUrl': audio_url,
            'episodeTitle': last_episode['title'],
            'author': last_episode['author'] if 'author' in last_episode else ""
        }
    except IndexError:
        print('could not find feed')
        return None

def get_episodes(feed_url, last=10):
    try:
        feed = feedparser.parse(feed_url)
        episodes = feed['entries'][:last]
        if feed['feed'] == {}: return 0
        return [episode['title'] for episode in episodes]
    except IndexError:
        print('could not find all last episodes')
        return 0
    
def get_language(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        return feed['feed']['language'][0:2]
    except KeyError:
        print('could not find feed or language key')
        return 0