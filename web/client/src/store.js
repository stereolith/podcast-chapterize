import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    jobId: '30a7b484-c42b-11e9-a83d-9cb6d0f0295f',
    currentStep: 'JOB RUNNING' // 'CHOOSE EPISODE', 'JOB RUNNING', 'DONE'
  },
  mutations: {
    setId(state, id) {
      state.jobId = id
    },
    setStep(state, status) {
      state.currentStep = status
    }
  },
  actions: {

  }
})
