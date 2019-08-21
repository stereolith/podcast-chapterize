<template>
<div class="border rounded-lg shadow-md p-4 my-10 bg-white">
  <div class="flex flex-col">

    <ChooseEpisode v-if="$store.state.currentStep === 'CHOOSE EPISODE'" />
    <JobStatus v-if="$store.state.currentStep === 'JOB RUNNING'" />
    <Player v-if="$store.state.currentStep === 'DONE'" />

  
  </div>
</div>
</template>

<script>
import ProgressBar from './ProgressBar'
import ChooseEpisode from './ChooseEpisode'
import JobStatus from './JobStatus'
import Player from './Player'

export default {
  name: 'ChapterizePanel',
  components: {
    ProgressBar,
    ChooseEpisode,
    JobStatus,
    Player
  },
  data () {
    return {
      feedUrl: '',
      
    }
  },
  computed: {
    jobId () {
      return this.$store.state.jobId
    }
  }
}
</script>
