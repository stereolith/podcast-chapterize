<template>
<div class="border rounded-lg shadow-md p-4 my-10 bg-white">
  <div class="flex flex-col">

    <ChooseEpisode v-if="jobId == ''"/>
    <JobStatus v-if="jobId != ''"/>


  
  </div>
</div>
</template>

<script>
import ProgressBar from './ProgressBar'
import ChooseEpisode from './ChooseEpisode'
import JobStatus from './JobStatus'

export default {
  name: 'ChapterizePanel',
  components: {
    ProgressBar,
    ChooseEpisode,
    JobStatus
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
