import Vue from 'vue'
import Vuex from 'vuex'

import { getJob } from './resources'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    jobId: '',
    currentStep: 'CHOOSE EPISODE', // 'CHOOSE EPISODE', 'JOB RUNNING', 'DONE'
    jobStatus: ''
  },
  mutations: {
    setId(state, id) {
      state.jobId = id
    },
    setStep(state, step) {
      state.currentStep = step
      if(step == 'CHOOSE EPISODE') state.jobId = ''
    },
    setJobStatus(state, status) {
      state.jobStatus = status
    }
  },
  actions: {
    updateStatus(context) {
      getJob(this.state.jobId)
      .then((res) => {
        context.commit('setJobStatus', res.data.data.job.status)

        if(res.data.data.job.status == 'DONE') {
          context.commit('setStep', 'DONE')
        } else if (res.data.data.job.status == 'TRANSCRIBING') {
          context.commit('setStep', 'JOB RUNNING')
        }
      })
      .catch((error) => {
        if (!error.response) {
          // network error
          console.log('network error')
          return
        }
        
        if (error.response.status === 404) {
          context.commit('setJobStatus', 'NOT_FOUND')
        } else {
          context.commit('setJobStatus', 'FAILED')
        }
      })
    }
  }
})
