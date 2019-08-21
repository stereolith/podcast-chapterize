import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    jobId: '96228656-c410-11e9-a83d-9cb6d0f0295f',
    currentStep: 'DONE' // 'CHOOSE EPISODE', 'JOB RUNNING', 'DONE'
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
