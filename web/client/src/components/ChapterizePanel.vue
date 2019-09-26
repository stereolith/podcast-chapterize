<template>
<div class="border rounded-lg shadow-md p-4 my-10 bg-white">
  <div class="flex flex-col">
    <div
      class="btn px-1 py-1 my-2 cursor-pointer text-gray-500 hover:text-gray-600 self-start "
      v-if="$store.state.currentStep != 'CHOOSE EPISODE'"
      @click="reset"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-left-circle"><circle cx="12" cy="12" r="10"></circle><polyline points="12 8 8 12 12 16"></polyline><line x1="16" y1="12" x2="8" y2="12"></line></svg>
    </div>   

    <ChooseEpisode v-if="$store.state.currentStep === 'CHOOSE EPISODE'" />
    <JobStatus v-if="$store.state.currentStep === 'JOB RUNNING'" />
    <Player v-if="$store.state.currentStep === 'DONE'" />

    <div 
      v-if="$store.state.currentStep === 'JOB RUNNING' || $store.state.currentStep === 'DONE'"
      class="text-center"
    >
      The unique ID of this job is <span class="bg-gray-300">{{$store.state.jobId}}</span></div>
    <div
      class="btn px-2 py-1 mt-5 hover:bg-gray-200 border rounded text-gray-600 text-sm font-bold text-center self-center"
      @click="findById = true"
    >
      find job by ID
    </div>
    <div v-if="findById" class="mt-3 flex items-center">
      <input
        v-model="customId"
        @change="handleIdInput"
        type="text"
        name=""
        id="customId"
        placeholder="job id"
        class="flex-1 bg-gray-200 active:bg-gray-400 p-2" 
      >
      <button @click="handleIdInput" class="btn px-3 text-gray-600"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg></button>
    </div>
    <div class="text-red-600" v-if="customId.length && $store.state.jobStatus === 'NOT_FOUND'">No transcription was found for this ID.</div>
  </div>
</div>
</template>

<script>
import { updateStatus } from '../resources'

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
      findById: false,
      customId: ''
    }
  },
  computed: {
    jobId () {
      return this.$store.state.jobId
    }
  },
  methods: {
    handleIdInput() {
      this.$store.commit('setId', this.customId)
      this.$store.dispatch('updateStatus')
    },
    reset() {
      this.findById = false
      this.customId = ''
      this.$store.commit('setStep', 'CHOOSE EPISODE')
    }
  }
}
</script>


<style>
input::placeholder {
  color: red;
}
</style>