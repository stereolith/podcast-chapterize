import axios from 'axios'

require('dotenv').config();
const baseDomain = process.env.HOST

const getJob = (_jobId) => axios.get(
    `${baseDomain}/job`,
    {
        params: {
            id: _jobId
        }
    }
)

const postJob = (_feedUrl, _episode, _language) => axios.post(
    `${baseDomain}/job`,
    {
        feedUrl: _feedUrl,
        episode: _episode,
        language: _language
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

const getLanguage = (_rssUrl) => axios.get(
    `${baseDomain}/feed-lang`,
    {
        params: {
            rssurl: _rssUrl
        }
    }
)

export { getJob, postJob, getEpisodes, getPlayerConfig, getLanguage, baseDomain }