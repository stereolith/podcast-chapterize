<template>
  <div class="flex flex-col">
    <div class="flex flex-col">
      <div class="flex flex-row items-center justify-center border-bottom my-4">
        <div class="h-10 w-10 rounded-full flex items-center justify-center bg-gray-200 text-xl mr-2">1</div>
        <h2 class="text-lg text-center">Enter a podcast RSS feed URL</h2>
      </div>
      <input type="text" v-model="feedUrl" placeholder="feed URL" :class="{'bg-red-200 border-red-200': urlError}" class="w-100 border bg-gray-200 text-gray-700 focus:border-pink-400 py-3 px-4"/>
      <div class="text-red-600" v-if="urlError">No podcast feed was forund for this URL.</div>
      <div v-if="loading" class="lds-ellipsis self-center"><div></div><div></div><div></div><div></div></div>
    </div>
    <div v-if="episodesFound" class="flex flex-col">
      <div class="flex flex-row items-center justify-center border-bottom my-4 mt-6">
        <div class="h-10 w-10 rounded-full flex items-center justify-center bg-gray-200 text-xl mr-2">2</div>
        <h2 class="text-lg text-center">Choose an episode</h2>
      </div>
      <select 
        v-model="selectedEpisode"
        name="episode"
        id="episodeSelect"
        class="block appearance-none w-full border text-gray-700 py-3 px-4 pr-8 bg-gray-200 focus:border-pink-400 focus:outline-none focus:bg-white focus:border-gray-500">
        <option
          v-for="episode in episodes"
          :value="episode.index"
          :key="episode.index"
        >
          {{episode.label}}
        </option>
      </select>
    </div>
    <button
      v-if="episodesFound && !jobStarted"
      @click="startJob"
      class="px-4 py-2 mt-8 bg-pink-400 rounded text-white font-bold w-1/3 self-center"
      :class="{'bg-gray-400 cursor-not-allowed': jobStarted}"
    >Start chapterize episode</button> 
    <div v-if="postError">There was an error when trying to start the chapterization.</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ChooseEpisode',
  data () {
    return {
      feedUrl: '',
      loading: false,
      episodesFound: false,
      episodes: [],
      selectedEpisode: 0,
      urlError: false,
      jobStarted: false,
      postError: false
    }
  },
  methods: {
    getEpisodes() {
      this.loading = true
      const path = 'http://localhost:5000/episodes'

      axios.get(path, {
        params: {
          rssurl: this.feedUrl
        }
      }).then((res) => {
        this.loading = false
        this.urlError = false
        this.episodesFound = true
        this.episodes = res.data.episodes
      })
      .catch((error) => {
        this.loading = false
        this.urlError = true
        console.error(error)
      });
    },
    startJob () {
      const path = 'http://localhost:5000/job'

      axios.post(path, {
          feedUrl: this.feedUrl,
          episode: this.selectedEpisode
      }).then((res) => {
        this.loading = false
        this.urlError = false
        this.episodesFound = true
        this.$store.commit('setId', res.data.jobId)
      })
      .catch((error) => {
        this.postError = true
        console.error(error)
      });
    }
  },
  watch: {
    feedUrl() {
      this.getEpisodes()
    }
  },
  mounted() {
    this.getEpisodes()
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
  background: #4a5568;
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
