<template>
<div class="flex flex-col">
  <h1 class="text-lg text-center font-bold py-3">Finished!</h1>

  <div class="flex justify-center">
    <a :href="audioUrl" target="_blank" class="px-4 py-2 my-4 mx-2 bg-gray-500 rounded inline-block text-white font-bold text-center self-center ">
      Download the chapterized Episode
    </a>
    <a :href="chapterUrl" target="_blank" class="px-4 py-2 my-4 mx-2 bg-gray-500 rounded inline-block text-white font-bold text-center self-center ">
      Download chapters text file
    </a>
  </div>
  
  <div id="player">

  </div>
</div>

</template>

<script>
import { getPlayerConfig, getJob, baseDomain } from '../resources'

import '../../public/js/web-player/embed'

export default {
  name: 'Player',
  data () {
    return {
      audioUrl: '',
      chapterUrl: ''
    }
  },
  mounted() {
    const path = 'http://localhost:5000/player-config'

    getPlayerConfig(this.$store.state.jobId)
    .then(res => {
      var config = res.data.config
      config.audio[0].url = baseDomain + '/' + config.audio[0].url
      this.initPlayer(config)
    })
    .catch((error) => {
      console.error(error)
    });

    getJob(this.$store.state.jobId)
    .then(res => {
      this.audioUrl = baseDomain + '/' + res.data.job.processedAudioFilePath
      this.chapterUrl = baseDomain + '/' + res.data.job.chaptersFilePath
    })
    .catch((error) => {
      console.error(error)
    });
  },
  methods: {
    initPlayer(config) {
      podlovePlayer('#player', config)
    }
  }
}
</script>
