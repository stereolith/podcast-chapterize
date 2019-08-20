import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    jobId: ''
  },
  mutations: {
    setId(state, id) {
      state.jobId = id
    }
  },
  actions: {

  }
})
