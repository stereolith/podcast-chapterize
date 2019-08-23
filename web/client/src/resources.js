import axios from 'axios'

const baseDomain = 'http://localhost:5000'

const getJob = (_jobId) => axios.get(
    `${baseDomain}/job`,
    {
        params: {
            id: _jobId
        }
    }
)

const postJob = (_feedUrl, _episode) => axios.post(
    `${baseDomain}/job`,
    {
        feedUrl: _feedUrl,
        episode: _episode
    }
)

const getEpisodes = (_rssUrl) => axios.get(
    `${baseDomain}/episodes`,
    {
        params: {
            rssurl: _rssUrl
        }
    }
)

const getPlayerConfig = (_jobId) => axios.get(
    `${baseDomain}/player-config`,
    {
        params: {
            id: _jobId
        }
    }
)

export { getJob, postJob, getEpisodes, getPlayerConfig }