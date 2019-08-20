<template>
  <div>
    <div class="flex flex-col">
      <h2 class="block text-lg text-center pt-5">Started chapterizing the episode</h2>
      <h3 class="block font-bold text-center">Check the status here</h3>
      
      <StatusBar 
        v-if="status != 'FAILED'"
        :states="['created', 'transcribing', 'NLP', 'writing chapters to file', 'done']"
        :activeState="statusIndex"
      />
      <div v-if="status === 'FAILED'">There was a problem.</div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'
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

      const path = 'http://localhost:5000/status'

      axios.get(path, {
        params: {
          id: this.$store.state.jobId
        }
      }).then((res) => {
        this.status = res.data.status.status
        if(this.status === 'FAILED' || this.status === 'DONE') clearInterval(interval)
        console.log(res.data.status.status)
      })
      .catch((error) => {
        console.error(error)
        clearInterval(interval)
      });

    },
    startIntervalPolling () {
      clearInterval(interval)
      interval = setInterval(this.getStatus.bind(this), 1000)
    }
  },
  computed: {
    statusIndex () {
      switch(this.status) {
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
    ...mapState(['jobId'])
  },
  mounted () {
    this.getStatus()
    this.startIntervalPolling()
  },
  watch: {
    jobId () {
      this.startIntervalPolling()
    }
  }
}
</script>


<style scoped lang="scss">

</style>
