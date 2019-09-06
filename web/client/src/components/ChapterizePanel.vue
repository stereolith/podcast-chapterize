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

    <choose-episode v-if="$store.state.currentStep === 'CHOOSE EPISODE'" />
    <job-status v-if="$store.state.currentStep === 'JOB RUNNING'" />
    <Player v-if="$store.state.currentStep === 'DONE'" />

    <div
      class="btn px-2 py-1 my-2 bg-gray-400 hover:bg-gray-500 rounded text-white text-sm font-bold text-center self-center"
      @click="findById = true"
    >
      enter job id manually
    </div>   
    <input
      v-if="findById"
      v-model="customId"
      @change="handleIdInput"
      type="text"
      name=""
      id="customId"
      placeholder="job id"
      class="bg-gray-300 active:bg-gray-500 p-2" 
    >
  </div>
</div>
</template>

<script>
import { updateStatus } from '../resources'

import ChooseEpisode from './ChooseEpisode'
import JobStatus from './JobStatus'
import Player from './Player'

export default {
  name: 'ChapterizePanel',
  components: {
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
