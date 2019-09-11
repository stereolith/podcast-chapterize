<template>
<div class="flex flex-col">
  <h1 class="text-lg text-center font-bold py-3">Finished!</h1>
  <a :href="audioUrl" target="_blank" class="px-4 py-2 my-4 bg-pink-400 hover:bg-pink-500 rounded text-white font-bold w-1/2 text-center self-center ">Download the chapterized Episode</a>
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
      audioUrl: ''
    }
  },
  mounted() {
    const path = 'http://localhost:5000/player-config'

    getPlayerConfig(this.$store.state.jobId)
    .then(res => {
      var config = res.data.config
      console.log(config)
      config.audio[0].url = baseDomain + '/' + config.audio[0].url
      this.initPlayer(config)
    })
    .catch((error) => {
      console.error(error)
    });

    getJob(this.$store.state.jobId)
    .then(res => {
      this.audioUrl = baseDomain + '/' + res.data.job.processedAudioFilePath
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
