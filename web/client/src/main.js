import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import "./main.css"

Vue.config.productionTip = false


// vuex
// - when id changes, update status
// - client-side persistence of jobId state
store.watch((state) => state.jobId, (_id) => {
    store.dispatch('updateStatus')
    localStorage.setItem('jobId', _id)
})
if (localStorage.getItem('jobId')) {
  store.commit('setId', localStorage.getItem('jobId'))
  console.log('commit')
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
