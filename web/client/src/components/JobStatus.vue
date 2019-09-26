<template>
  <div>
    <div class="flex flex-col">
      <h2 class="block text-lg text-center pt-5">Started chapterizing the episode</h2>
      <h3 class="block text-center">Check the status here:</h3>
      
      <div v-if="loading" class="lds-ellipsis self-center"><div></div><div></div><div></div><div></div></div>
      <StatusBar 
        v-if="this.$store.state.jobStatus != 'FAILED'"
        :states="['created', 'transcribing', 'NLP', 'writing chapters to file', 'done']"
        :activeState="statusIndex"
      />
      <div v-if="this.$store.state.jobStatus === 'FAILED' && !loading">There was a problem.</div>

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
      loading: true      
    }
  },
  
  methods: {
    getStatus () {

      this.$store.dispatch('updateStatus')
      this.loading = false

    },
    startIntervalPolling () {
      clearInterval(interval)
      interval = setInterval(this.getStatus.bind(this), 10000)
      setTimeout(() => this.loading = false, 2000)
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
    this.startIntervalPolling()
  },
  beforeDestroy () {
    clearInterval(interval)
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


<style scoped>
.lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}
.lds-ellipsis div {
  position: absolute;
  top: 27px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #fff;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.lds-ellipsis div:nth-child(1) {
  left: 6px;
  animation: lds-ellipsis1 0.6s infinite;
}
.lds-ellipsis div:nth-child(2) {
  left: 6px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(3) {
  left: 26px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(4) {
  left: 45px;
  animation: lds-ellipsis3 0.6s infinite;
}
@keyframes lds-ellipsis1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes lds-ellipsis3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}
@keyframes lds-ellipsis2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(19px, 0);
  }
}

</style>
