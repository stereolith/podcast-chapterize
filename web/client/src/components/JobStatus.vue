<template>
  <div>
    <div class="flex flex-col">
      <h2 class="block text-lg text-center pt-5">Started chapterizing the episode</h2>
      <h3 class="block font-bold text-center">Check the status here</h3>
      
      <StatusBar 
        v-if="this.$store.state.jobStatus != 'FAILED'"
        :states="['created', 'transcribing', 'NLP', 'writing chapters to file', 'done']"
        :activeState="statusIndex"
      />
      <div v-if="this.$store.state.jobStatus === 'FAILED'">There was a problem.</div>

    </div>
  </div>
</template>

<script>
import { getJob } from '../resources'
import { mapState } from 'vuex';

import StatusBar from './StatusBar'

var interval

export default {
  name: 'JobStatus',
  components: {
    StatusBar
  },
  data () {
    return {
      status: ''      
    }
  },
  
  methods: {
    getStatus () {

      this.$store.dispatch('updateStatus')

    },
    startIntervalPolling () {
      clearInterval(interval)
      interval = setInterval(this.getStatus.bind(this), 10000)
    }
  },
  computed: {
    statusIndex () {
      switch(this.$store.state.jobStatus) {
        case 'CREATED':
          return 0
        case 'TRANSCRIBING':
          return 1
        case 'NLP':
          return 2
        case 'WRITING CHAPTERS':
          return 3
        case 'DONE':
          return 4
      }
    },
    ...mapState(['jobId', 'jobStatus', 'statusError'])
  },
  mounted () {
    this.getStatus()
    this.startIntervalPolling()
  },
  watch: {
    jobId () {
      this.startIntervalPolling()
    },
    jobStatus (newStatus) {
      if(newStatus === 'FAILED' || newStatus === 'DONE') {
        clearInterval(interval)
      }
    },
    statusError (error) {
      if (error) {
        clearInterval(interval)
      }
    }
  }
}
</script>


<style scoped lang="scss">

</style>
